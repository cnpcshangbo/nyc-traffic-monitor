import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
from pathlib import Path
import time
import subprocess
import tempfile
import os

# Fix for PyTorch 2.6+ weights_only default change
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, model_path: str):
        """Initialize YOLOv8 model for video processing"""
        self.model = None
        try:
            logger.info(f"Loading YOLO model from: {model_path}")
            self.model = YOLO(model_path)
            logger.info("Model loaded successfully")
            
            if hasattr(self.model, 'names'):
                logger.info(f"Model classes: {self.model.names}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def process_video(self, input_path: str, output_path: str, conf_threshold: float = 0.3):
        """
        Process video with YOLOv8 and save with bounding boxes
        
        Args:
            input_path: Path to input video
            output_path: Path to save processed video
            conf_threshold: Confidence threshold for detections
        """
        try:
            logger.info(f"Processing video: {input_path}")
            
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {input_path}")
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Create temporary file for raw frames
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Use mp4v for temporary processing (faster)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                
                frame_count = 0
                start_time = time.time()
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    results = self.model(frame, conf=conf_threshold, verbose=False)
                    
                    annotated_frame = self.draw_bounding_boxes(frame, results[0])
                    
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
                
                # Convert to web-compatible format using ffmpeg
                logger.info("Converting to web-compatible format...")
                ffmpeg_cmd = [
                    'ffmpeg', '-y',  # -y to overwrite output file
                    '-i', temp_path,
                    '-c:v', 'libx264',  # H.264 video codec
                    '-preset', 'fast',  # Encoding speed
                    '-crf', '23',       # Constant Rate Factor (quality)
                    '-movflags', '+faststart',  # Web optimization
                    '-pix_fmt', 'yuv420p',      # Web-compatible pixel format
                    output_path
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    # Fallback: just copy the temp file
                    import shutil
                    shutil.move(temp_path, output_path)
                    logger.warning("Used fallback encoding (may not be web-compatible)")
                else:
                    logger.info("Successfully converted to web-compatible format")
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            elapsed = time.time() - start_time
            logger.info(f"Video processing completed in {elapsed:.2f}s")
            logger.info(f"Output saved to: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")
            raise
    
    def draw_bounding_boxes(self, frame, results):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            results: YOLO detection results
        
        Returns:
            Frame with bounding boxes drawn
        """
        annotated_frame = frame.copy()
        
        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                if hasattr(self.model, 'names') and cls in self.model.names:
                    label = self.model.names[cls]
                else:
                    label = f"class_{cls}"
                
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
    
    def get_color_for_class(self, class_name: str):
        """
        Get color for different traffic classes
        
        Args:
            class_name: Name of the detected class
        
        Returns:
            BGR color tuple
        """
        colors = {
            'car': (0, 255, 0),        # Green
            'truck': (0, 0, 255),       # Red
            'bus': (255, 0, 0),         # Blue
            'motorcycle': (255, 255, 0), # Cyan
            'bicycle': (255, 0, 255),    # Magenta
            'person': (0, 255, 255),     # Yellow
            'pedestrian': (0, 255, 255), # Yellow
        }
        
        class_lower = class_name.lower()
        for key, color in colors.items():
            if key in class_lower:
                return color
        
        return (128, 128, 128)
    
    def process_frame(self, frame, conf_threshold: float = 0.3):
        """
        Process a single frame and return detections
        
        Args:
            frame: Input frame
            conf_threshold: Confidence threshold
        
        Returns:
            Detection results
        """
        results = self.model(frame, conf=conf_threshold, verbose=False)
        return results[0]