#!/usr/bin/env python3
"""
Script to reprocess Columbus-86th video with improved detection parameters
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.video_processor import VideoProcessor
from pathlib import Path
import logging
import cv2
import numpy as np
import torch
from ultralytics import YOLO

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

class ImprovedVideoProcessor(VideoProcessor):
    def __init__(self, model_path: str):
        super().__init__(model_path)
        
    def process_video(self, input_path: str, output_path: str, conf_threshold: float = 0.5):
        """
        Process video with improved detection parameters
        
        Args:
            input_path: Path to input video
            output_path: Path to save processed video
            conf_threshold: Confidence threshold for detections (increased from 0.3)
        """
        try:
            logger.info(f"Processing video with improved parameters: {input_path}")
            
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {input_path}")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Define exclusion zones for Columbus-86th (problematic right side area)
            exclusion_zones = []
            if "Columbus-86th" in input_path:
                # Exclude right side area where false detections occur
                exclusion_zones.append({
                    'x1': int(width * 0.75),  # Right 25% of frame
                    'y1': 0,
                    'x2': width,
                    'y2': int(height * 0.6)   # Upper 60% of right side
                })
                logger.info("Added exclusion zone for Columbus-86th problematic area")
            
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                
                frame_count = 0
                import time
                start_time = time.time()
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Use improved YOLO parameters
                    results = self.model(
                        frame, 
                        conf=conf_threshold,           # Higher confidence threshold
                        iou=0.5,                       # NMS IoU threshold
                        max_det=50,                    # Limit max detections per frame
                        verbose=False
                    )
                    
                    annotated_frame = self.draw_improved_bounding_boxes(
                        frame, results[0], exclusion_zones, width, height
                    )
                    
                    out.write(annotated_frame)
                    
                    frame_count += 1
                    if frame_count % 30 == 0:
                        elapsed = time.time() - start_time
                        fps_actual = frame_count / elapsed
                        progress = (frame_count / total_frames) * 100
                        logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) - {fps_actual:.1f} FPS")
                
                cap.release()
                out.release()
                cv2.destroyAllWindows()
                
                # Convert to web-compatible format
                logger.info("Converting to web-compatible format...")
                import subprocess
                ffmpeg_cmd = [
                    'ffmpeg', '-y',
                    '-i', temp_path,
                    '-c:v', 'libx264',
                    '-preset', 'fast',
                    '-crf', '23',
                    '-movflags', '+faststart',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    import shutil
                    shutil.move(temp_path, output_path)
                    logger.warning("Used fallback encoding")
                else:
                    logger.info("Successfully converted to web-compatible format")
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            elapsed = time.time() - start_time
            logger.info(f"Improved video processing completed in {elapsed:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise
    
    def draw_improved_bounding_boxes(self, frame, results, exclusion_zones=None, frame_width=0, frame_height=0):
        """
        Draw bounding boxes with improved filtering
        
        Args:
            frame: Input frame
            results: YOLO detection results
            exclusion_zones: List of zones to exclude detections from
            frame_width: Frame width for size filtering
            frame_height: Frame height for size filtering
        
        Returns:
            Frame with filtered bounding boxes drawn
        """
        annotated_frame = frame.copy()
        
        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                # Get class label
                if hasattr(self.model, 'names') and cls in self.model.names:
                    label = self.model.names[cls]
                else:
                    label = f"class_{cls}"
                
                # Filter 1: Check if detection is in exclusion zone
                if exclusion_zones:
                    in_exclusion = False
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    for zone in exclusion_zones:
                        if (zone['x1'] <= center_x <= zone['x2'] and 
                            zone['y1'] <= center_y <= zone['y2']):
                            in_exclusion = True
                            break
                    
                    if in_exclusion:
                        logger.debug(f"Filtered out {label} in exclusion zone")
                        continue
                
                # Filter 2: Size-based filtering
                box_width = x2 - x1
                box_height = y2 - y1
                box_area = box_width * box_height
                
                # Filter out boxes that are too large (likely false detections)
                if frame_width > 0 and frame_height > 0:
                    frame_area = frame_width * frame_height
                    relative_area = box_area / frame_area
                    
                    # Filter out detections larger than 40% of frame (unrealistic for vehicles)
                    if relative_area > 0.4:
                        logger.debug(f"Filtered out oversized {label} (area: {relative_area:.2%})")
                        continue
                    
                    # Filter out very small detections (likely noise)
                    if relative_area < 0.001:
                        logger.debug(f"Filtered out undersized {label} (area: {relative_area:.2%})")
                        continue
                
                # Filter 3: Aspect ratio filtering
                aspect_ratio = box_width / box_height if box_height > 0 else 0
                
                # Reasonable aspect ratios for vehicles (0.5 to 4.0)
                if aspect_ratio < 0.5 or aspect_ratio > 4.0:
                    logger.debug(f"Filtered out {label} with unrealistic aspect ratio: {aspect_ratio:.2f}")
                    continue
                
                # Draw the bounding box if it passes all filters
                color = self.get_color_for_class(label)
                
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                label_text = f"{label} {conf:.2f}"
                label_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_y = y1 - 10 if y1 - 10 > 0 else y1 + 20
                
                cv2.rectangle(annotated_frame, 
                            (x1, label_y - label_size[1] - 4),
                            (x1 + label_size[0], label_y + 4),
                            color, -1)
                
                cv2.putText(annotated_frame, label_text,
                          (x1, label_y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated_frame

def main():
    """Reprocess Columbus-86th video with improved parameters"""
    
    processor = ImprovedVideoProcessor(MODEL_PATH)
    
    # Process Columbus-86th with improved parameters
    video_info = {
        "location": "Columbus-86th",
        "filename": "2025-02-13_06-00-06.mp4"
    }
    
    # Use videos from backend/videos directory
    input_path = f"videos/{video_info['location']}_{video_info['filename']}"
    output_filename = f"{video_info['location']}_{video_info['filename'].replace('.mp4', '_improved.mp4')}"
    output_path = Path("processed_videos") / output_filename
    
    if not os.path.exists(input_path):
        logger.error(f"Video not found: {input_path}")
        return
    
    try:
        logger.info(f"Reprocessing {video_info['location']} with improved parameters...")
        
        # Use higher confidence threshold and improved filtering
        processor.process_video(input_path, str(output_path), conf_threshold=0.6)
        
        logger.info(f"Successfully reprocessed {video_info['location']} -> {output_path}")
        
        # Optionally replace the original processed file
        original_path = Path("processed_videos") / f"{video_info['location']}_{video_info['filename'].replace('.mp4', '_processed.mp4')}"
        if original_path.exists():
            backup_path = Path("processed_videos") / f"{video_info['location']}_{video_info['filename'].replace('.mp4', '_processed_backup.mp4')}"
            os.rename(str(original_path), str(backup_path))
            os.rename(str(output_path), str(original_path))
            logger.info(f"Replaced original processed video (backup created)")
            
    except Exception as e:
        logger.error(f"Failed to reprocess {video_info['location']}: {e}")

if __name__ == "__main__":
    main()