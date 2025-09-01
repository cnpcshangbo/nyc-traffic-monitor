#!/usr/bin/env python3
"""
Enhanced Video Processor with Virtual Inductive Loop System
Processes videos with YOLOv8 detection and traffic volume counting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import time

from virtual_loop import VirtualLoopSystem, VirtualInductiveLoop, VehicleDetection
from loop_configs import get_loop_config, validate_loop_config

# Fix for PyTorch 2.6+ weights_only default change
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

logger = logging.getLogger(__name__)

class VideoProcessorWithLoops:
    """Enhanced video processor with virtual inductive loop system"""
    
    def __init__(self, model_path: str, location_id: str):
        """
        Initialize processor with YOLO model and virtual loops
        
        Args:
            model_path: Path to YOLOv8 model file
            location_id: Location identifier for loop configuration
        """
        self.model_path = model_path
        self.location_id = location_id
        self.model = None
        self.loop_system = None
        self.exclusion_zones = []
        
        # Load YOLO model
        try:
            logger.info(f"Loading YOLO model from: {model_path}")
            self.model = YOLO(model_path)
            logger.info("Model loaded successfully")
            
            if hasattr(self.model, 'names'):
                logger.info(f"Model classes: {self.model.names}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
            
        # Initialize virtual loop system
        self.setup_virtual_loops()
        
    def setup_virtual_loops(self):
        """Setup virtual inductive loops for the location"""
        self.loop_system = VirtualLoopSystem(self.location_id)
        
        # Get loop configuration for this location
        loop_configs = get_loop_config(self.location_id)
        
        if not loop_configs:
            logger.warning(f"No virtual loop configuration found for location: {self.location_id}")
            return
            
        # Create and add virtual loops
        for config in loop_configs:
            if not validate_loop_config(config):
                logger.error(f"Invalid loop configuration: {config}")
                continue
                
            loop = VirtualInductiveLoop(
                name=config["name"],
                zone_points=config["zone_points"],
                direction=config["direction"]
            )
            self.loop_system.add_loop(loop)
            
        logger.info(f"Initialized {len(self.loop_system.loops)} virtual loops for {self.location_id}")
        
    def add_exclusion_zone(self, zone: Dict[str, int]):
        """Add exclusion zone for false detections"""
        self.exclusion_zones.append(zone)
        logger.info(f"Added exclusion zone: {zone}")
        
    def is_in_exclusion_zone(self, bbox: List[int], zones: List[Dict]) -> bool:
        """Check if detection is in any exclusion zone"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        for zone in zones:
            if (zone['x1'] <= center_x <= zone['x2'] and 
                zone['y1'] <= center_y <= zone['y2']):
                return True
        return False
        
    def is_valid_detection(self, bbox: List[int], conf: float, class_name: str, 
                          width: int, height: int) -> bool:
        """Validate detection with enhanced filtering"""
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
                return False
                
            # Reject detections with extreme aspect ratios (likely vertical objects)
            aspect_ratio = det_width / det_height if det_height > 0 else 0
            if aspect_ratio < 0.3 or aspect_ratio > 4.0:
                return False
                
            # Higher confidence threshold for bikes/motorcycles
            if conf < 0.7:
                return False
                
        return True
        
    def process_frame_detections(self, frame: np.ndarray, frame_number: int, 
                               timestamp: float, conf_threshold: float = 0.5) -> List[VehicleDetection]:
        """
        Process a single frame and return valid detections
        
        Args:
            frame: Input video frame
            frame_number: Frame number in video
            timestamp: Timestamp in seconds
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of VehicleDetection objects
        """
        height, width = frame.shape[:2]
        
        # Run YOLO detection
        results = self.model(
            frame, 
            conf=conf_threshold,
            iou=0.4,  # Lower IoU for better NMS
            max_det=30,  # Limit detections
            verbose=False
        )
        
        detections = []
        detection_id = 0
        
        # Process YOLO results
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
                    
                    # Apply validation filters
                    if not self.is_valid_detection(bbox, conf, class_name, width, height):
                        continue
                    
                    # Calculate centroid
                    x1, y1, x2, y2 = bbox
                    centroid = ((x1 + x2) // 2, (y1 + y2) // 2)
                    
                    # Create detection object
                    detection = VehicleDetection(
                        id=detection_id,
                        class_name=class_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        centroid=centroid,
                        timestamp=timestamp,
                        frame_number=frame_number
                    )
                    detections.append(detection)
                    detection_id += 1
        
        return detections
        
    def draw_detections_and_loops(self, frame: np.ndarray, detections: List[VehicleDetection]) -> np.ndarray:
        """Draw detections and virtual loops on frame"""
        
        # Draw virtual loops
        if self.loop_system:
            frame = self.loop_system.draw_loops(frame)
        
        # Draw detections
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            
            # Color by class
            colors = {
                'pc': (0, 255, 0),      # Green
                'truck': (0, 0, 255),   # Red
                'bus': (255, 0, 0),     # Blue
                'bk/mc': (0, 255, 255), # Yellow
                'ped': (255, 165, 0),   # Orange
            }
            color = colors.get(detection.class_name.lower(), (128, 128, 128))
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{detection.class_name}: {detection.confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
        
    def process_video_with_loops(self, input_path: str, output_video_path: str, 
                                output_json_path: str, conf_threshold: float = 0.6) -> bool:
        """
        Process video with virtual inductive loops and export results
        
        Args:
            input_path: Input video file path
            output_video_path: Output processed video path (web-compatible)
            output_json_path: Output JSON data path
            conf_threshold: Detection confidence threshold
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            logger.info(f"Processing video with virtual loops: {input_path}")
            
            # Open video
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {input_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video specs: {width}x{height}, {fps}fps, {total_frames} frames")
            
            # Set video FPS in loop system
            if self.loop_system:
                self.loop_system.video_fps = fps
            
            # Add location-specific exclusion zones
            self.add_location_exclusion_zones(width, height)
            
            # Create temporary video file
            temp_dir = tempfile.mkdtemp()
            temp_video = os.path.join(temp_dir, "temp_processed.avi")
            
            try:
                # Use AVI format for OpenCV processing (more compatible)
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
                
                frame_number = 0
                start_time = time.time()
                
                logger.info("Starting frame-by-frame processing...")
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Calculate timestamp
                    timestamp = frame_number / fps
                    
                    # Process detections for this frame
                    detections = self.process_frame_detections(
                        frame, frame_number, timestamp, conf_threshold
                    )
                    
                    # Update virtual loop system
                    if self.loop_system and detections:
                        new_crossings = self.loop_system.process_detections(detections, frame_number)
                        if new_crossings:
                            logger.debug(f"Frame {frame_number}: {len(new_crossings)} new crossings")
                    
                    # Draw detections and loops on frame
                    frame = self.draw_detections_and_loops(frame, detections)
                    
                    # Write frame
                    out.write(frame)
                    frame_number += 1
                    
                    # Progress logging
                    if frame_number % (fps * 10) == 0:  # Every 10 seconds
                        elapsed = time.time() - start_time
                        progress = (frame_number / total_frames) * 100
                        eta = (elapsed / frame_number) * (total_frames - frame_number)
                        logger.info(f"Progress: {progress:.1f}% ({frame_number}/{total_frames}), ETA: {eta:.1f}s")
                
                cap.release()
                out.release()
                
                # Convert to web-compatible MP4 using FFmpeg
                logger.info("Converting to web-compatible MP4 format...")
                ffmpeg_cmd = [
                    'ffmpeg', '-i', temp_video, 
                    '-c:v', 'libx264',           # H.264 codec for web compatibility
                    '-preset', 'medium',         # Encoding speed/quality balance
                    '-crf', '23',                # Quality setting
                    '-movflags', '+faststart',   # Web streaming optimization
                    '-y',                        # Overwrite output
                    output_video_path
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
                
                # Export traffic data to JSON
                if self.loop_system:
                    logger.info("Exporting traffic data to JSON...")
                    json_success = self.loop_system.export_to_json(output_json_path, interval_seconds=15)
                    
                    if json_success:
                        # Log summary statistics
                        stats = self.loop_system.get_summary_stats()
                        logger.info(f"Traffic counting summary:")
                        logger.info(f"  Total crossings: {stats['total_crossings']}")
                        logger.info(f"  Crossings by class: {stats['crossings_by_class']}")
                        logger.info(f"  Crossings by loop: {stats['crossings_by_loop']}")
                
                # Clean up temp files
                os.unlink(temp_video)
                os.rmdir(temp_dir)
                
                elapsed_total = time.time() - start_time
                logger.info(f"✅ Processing completed in {elapsed_total:.1f}s")
                logger.info(f"✅ Video saved: {output_video_path}")
                logger.info(f"✅ Data saved: {output_json_path}")
                
                # Check output file sizes
                if os.path.exists(output_video_path):
                    video_size = os.path.getsize(output_video_path) / (1024 * 1024)  # MB
                    logger.info(f"Output video size: {video_size:.1f} MB")
                
                if os.path.exists(output_json_path):
                    json_size = os.path.getsize(output_json_path) / 1024  # KB
                    logger.info(f"Output JSON size: {json_size:.1f} KB")
                
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
            
    def add_location_exclusion_zones(self, width: int, height: int):
        """Add exclusion zones specific to each location"""
        
        if self.location_id == "74th-Amsterdam-Columbus":
            # Richmond Hill Road - traffic light exclusion zone
            self.add_exclusion_zone({
                'x1': 1715,
                'y1': 347,
                'x2': 1915,
                'y2': 547
            })
            
        elif self.location_id == "Columbus-86th":
            # Katonah Ave - exclude problematic areas
            self.add_exclusion_zone({
                'x1': int(width * 0.75),  # Right 25%
                'y1': 0,
                'x2': width,
                'y2': int(height * 0.6)   # Upper 60%
            })
            
        # Add more location-specific exclusions as needed