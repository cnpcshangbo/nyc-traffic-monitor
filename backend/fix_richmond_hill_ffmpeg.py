#!/usr/bin/env python3
"""
Script to fix false traffic light detection in Richmond Hill Road video
Uses FFmpeg for better codec compatibility
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
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

class ImprovedRichmondHillProcessor(VideoProcessor):
    def __init__(self, model_path: str):
        super().__init__(model_path)
        self.exclusion_zones = []
        
    def add_exclusion_zone(self, zone):
        """Add exclusion zone for false detections"""
        self.exclusion_zones.append(zone)
        logger.info(f"Added exclusion zone: {zone}")
        
    def is_in_exclusion_zone(self, bbox, zones):
        """Check if detection is in any exclusion zone"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        for zone in zones:
            if (zone['x1'] <= center_x <= zone['x2'] and 
                zone['y1'] <= center_y <= zone['y2']):
                return True
        return False
        
    def is_valid_detection(self, bbox, conf, class_name, width, height):
        """Validate detection with improved filtering"""
        x1, y1, x2, y2 = bbox
        
        # Basic size validation
        det_width = x2 - x1
        det_height = y2 - y1
        
        if det_width < 10 or det_height < 10:
            return False
            
        # Check exclusion zones
        if self.is_in_exclusion_zone(bbox, self.exclusion_zones):
            return False
            
        # Enhanced filtering for bike/motorcycle false positives
        if class_name.lower() in ['bicycle', 'motorcycle', 'bike', 'bk', 'mc', 'bk/mc']:
            # Reject very small detections that could be traffic lights/signs
            min_size_threshold = min(width, height) * 0.02  # 2% of frame size
            if det_width < min_size_threshold or det_height < min_size_threshold:
                logger.debug(f"Rejected small {class_name}: size {det_width}x{det_height} < {min_size_threshold}")
                return False
                
            # Reject detections with extreme aspect ratios (likely vertical objects like poles/lights)
            aspect_ratio = det_width / det_height if det_height > 0 else 0
            if aspect_ratio < 0.3 or aspect_ratio > 4.0:
                logger.debug(f"Rejected {class_name}: extreme aspect ratio {aspect_ratio:.2f}")
                return False
                
            # Higher confidence threshold for bikes/motorcycles
            if conf < 0.7:
                logger.debug(f"Rejected {class_name}: low confidence {conf:.2f}")
                return False
                
        return True

    def process_video_with_ffmpeg(self, input_path: str, output_path: str, conf_threshold: float = 0.65):
        """
        Process video and use FFmpeg for encoding to ensure web compatibility
        """
        try:
            logger.info(f"Processing Richmond Hill Road video: {input_path}")
            
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {input_path}")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video specs: {width}x{height}, {fps}fps, {total_frames} frames")
            
            # Add precise exclusion zone based on analysis: traffic light at (1816, 447)
            self.add_exclusion_zone({
                'x1': 1715,  # Analysis suggested: 1716-1916
                'y1': 347,   # Analysis suggested: 347-547  
                'x2': 1915,
                'y2': 547
            })
            logger.info("Added precise traffic light exclusion zone for Richmond Hill Road at (1715,347)-(1915,547)")
            
            # Create temporary directory for frames
            import tempfile
            temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(temp_dir, "temp_processed.avi")
            
            try:
                # Use AVI format for OpenCV processing (more compatible)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
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
                        iou=0.4,                       # Lower IoU for better NMS
                        max_det=30,                    # Limit detections
                        verbose=False
                    )
                    
                    # Process detections with enhanced filtering
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                # Get detection data
                                bbox = box.xyxy[0].cpu().numpy().astype(int)
                                conf = float(box.conf[0])
                                cls_id = int(box.cls[0])
                                
                                # Get class name
                                if hasattr(self.model, 'names') and cls_id in self.model.names:
                                    class_name = self.model.names[cls_id]
                                else:
                                    class_name = f"class_{cls_id}"
                                
                                # Apply enhanced validation
                                if not self.is_valid_detection(bbox, conf, class_name, width, height):
                                    continue
                                
                                # Draw bounding box
                                x1, y1, x2, y2 = bbox
                                color = self.get_color_for_class(class_name)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                
                                # Draw label
                                label = f"{class_name}: {conf:.2f}"
                                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                            (x1 + label_size[0], y1), color, -1)
                                cv2.putText(frame, label, (x1, y1 - 5), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    out.write(frame)
                    frame_count += 1
                    
                    # Progress logging
                    if frame_count % (fps * 10) == 0:  # Every 10 seconds
                        elapsed = time.time() - start_time
                        progress = (frame_count / total_frames) * 100
                        eta = (elapsed / frame_count) * (total_frames - frame_count)
                        logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}), ETA: {eta:.1f}s")
                
                cap.release()
                out.release()
                
                # Convert to web-compatible MP4 using FFmpeg
                logger.info("Converting to web-compatible MP4 format...")
                ffmpeg_cmd = [
                    'ffmpeg', '-i', temp_video, 
                    '-c:v', 'libx264',           # H.264 codec
                    '-preset', 'medium',         # Encoding speed/quality balance
                    '-crf', '23',                # Quality setting
                    '-movflags', '+faststart',   # Web streaming optimization
                    '-y',                        # Overwrite output
                    output_path
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    return False
                
                # Clean up temp files
                os.unlink(temp_video)
                os.rmdir(temp_dir)
                
                elapsed_total = time.time() - start_time
                logger.info(f"✅ Processing completed in {elapsed_total:.1f}s")
                logger.info(f"✅ Saved: {output_path}")
                
                # Check file size
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                    logger.info(f"Output file size: {file_size:.1f} MB")
                
                return True
                
            except Exception as e:
                # Clean up temp files on error
                if os.path.exists(temp_video):
                    os.unlink(temp_video)
                if os.path.exists(temp_dir):
                    os.rmdir(temp_dir)
                raise e
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            return False
    
    def get_color_for_class(self, class_name):
        """Get color for bounding box based on class"""
        colors = {
            'car': (0, 255, 0),      # Green
            'pc': (0, 255, 0),       # Green (Personal Car)
            'truck': (0, 0, 255),    # Red  
            'bus': (255, 0, 0),      # Blue
            'motorcycle': (0, 255, 255),  # Yellow
            'bicycle': (255, 0, 255),     # Magenta
            'bk/mc': (0, 255, 255),       # Yellow
            'person': (255, 165, 0),      # Orange
            'ped': (255, 165, 0),         # Orange (Pedestrian)
        }
        return colors.get(class_name.lower(), (128, 128, 128))  # Gray default

def main():
    """Main processing function"""
    # Input and output paths
    input_video = "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    output_video = "processed_videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04_processed_fixed.mp4"
    
    if not os.path.exists(input_video):
        logger.error(f"Input video not found: {input_video}")
        return False
    
    # Initialize processor
    processor = ImprovedRichmondHillProcessor(MODEL_PATH)
    
    # Process video with improved parameters
    success = processor.process_video_with_ffmpeg(input_video, output_video, conf_threshold=0.65)
    
    if success:
        logger.info("✅ Richmond Hill Road video processing completed successfully!")
        
        # Replace the original processed video
        backup_video = "processed_videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04_processed_original.mp4"
        original_video = "processed_videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04_processed.mp4"
        
        if os.path.exists(original_video):
            os.rename(original_video, backup_video)
            logger.info(f"Backed up original to: {backup_video}")
            
        os.rename(output_video, original_video)
        logger.info(f"Replaced original with fixed version: {original_video}")
        
    else:
        logger.error("❌ Processing failed")
    
    return success

if __name__ == "__main__":
    main()