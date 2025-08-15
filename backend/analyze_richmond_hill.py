#!/usr/bin/env python3
"""
Quick analysis script to identify false detections in Richmond Hill Road video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for PyTorch weights_only issue
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def analyze_video():
    """Analyze first 30 seconds to identify false detections"""
    
    input_video = "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    
    if not os.path.exists(input_video):
        logger.error(f"Video not found: {input_video}")
        return
    
    # Load model
    logger.info("Loading YOLO model...")
    model = YOLO(MODEL_PATH)
    
    cap = cv2.VideoCapture(input_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video: {width}x{height}, {fps}fps")
    
    frame_count = 0
    bike_mc_detections = []
    
    # Analyze first 30 seconds
    max_frames = fps * 30
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run detection every 30 frames (1 second intervals)
        if frame_count % 30 == 0:
            results = model(frame, conf=0.3, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        bbox = box.xyxy[0].cpu().numpy().astype(int)
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        
                        if hasattr(model, 'names') and cls_id in model.names:
                            class_name = model.names[cls_id]
                        else:
                            class_name = f"class_{cls_id}"
                        
                        # Look for bike/motorcycle false detections
                        if any(keyword in class_name.lower() for keyword in ['bike', 'bicycle', 'motorcycle', 'bk', 'mc']):
                            x1, y1, x2, y2 = bbox
                            det_width = x2 - x1
                            det_height = y2 - y1
                            
                            detection_info = {
                                'frame': frame_count,
                                'time': frame_count / fps,
                                'class': class_name,
                                'conf': conf,
                                'bbox': bbox,
                                'size': (det_width, det_height),
                                'position': ((x1 + x2) // 2, (y1 + y2) // 2),
                                'aspect_ratio': det_width / det_height if det_height > 0 else 0
                            }
                            bike_mc_detections.append(detection_info)
                            
                            logger.info(f"Frame {frame_count} ({frame_count/fps:.1f}s): {class_name} "
                                      f"conf={conf:.2f} pos=({(x1+x2)//2},{(y1+y2)//2}) "
                                      f"size={det_width}x{det_height} aspect={det_width/det_height:.2f}")
        
        frame_count += 1
    
    cap.release()
    
    # Analyze patterns
    logger.info(f"\n=== ANALYSIS RESULTS ===")
    logger.info(f"Total bike/motorcycle detections: {len(bike_mc_detections)}")
    
    if bike_mc_detections:
        # Group by position to find persistent false detections
        position_groups = {}
        for det in bike_mc_detections:
            pos_key = f"{det['position'][0]//50}_{det['position'][1]//50}"  # Group by 50px regions
            if pos_key not in position_groups:
                position_groups[pos_key] = []
            position_groups[pos_key].append(det)
        
        # Find most frequent false detection areas
        logger.info("\n=== FREQUENT DETECTION AREAS ===")
        for pos_key, detections in position_groups.items():
            if len(detections) >= 3:  # Appears in 3+ frames
                avg_pos = np.mean([d['position'] for d in detections], axis=0)
                avg_conf = np.mean([d['conf'] for d in detections])
                avg_size = np.mean([d['size'] for d in detections], axis=0)
                classes = [d['class'] for d in detections]
                
                logger.info(f"Persistent area: pos=({avg_pos[0]:.0f},{avg_pos[1]:.0f}) "
                          f"count={len(detections)} avg_conf={avg_conf:.2f} "
                          f"avg_size={avg_size[0]:.0f}x{avg_size[1]:.0f} classes={set(classes)}")
                
                # Suggest exclusion zone
                margin = 100
                zone_x1 = max(0, int(avg_pos[0] - margin))
                zone_y1 = max(0, int(avg_pos[1] - margin))
                zone_x2 = min(width, int(avg_pos[0] + margin))
                zone_y2 = min(height, int(avg_pos[1] + margin))
                
                logger.info(f"Suggested exclusion zone: x1={zone_x1} y1={zone_y1} x2={zone_x2} y2={zone_y2}")

if __name__ == "__main__":
    analyze_video()