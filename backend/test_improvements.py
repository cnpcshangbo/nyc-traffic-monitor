#!/usr/bin/env python3
"""
Quick test script to process first 5 seconds of Columbus-86th video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import torch
from ultralytics import YOLO
import logging

# Fix for PyTorch 2.6+ weights_only default change
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def quick_test():
    """Process first 5 seconds to test improvements"""
    
    model = YOLO(MODEL_PATH)
    logger.info("Model loaded successfully")
    
    input_path = "videos/Columbus-86th_2025-02-13_06-00-06.mp4"
    output_path = "processed_videos/Columbus-86th_test_5sec.mp4"
    
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        logger.error(f"Cannot open video: {input_path}")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video: {width}x{height} @ {fps}fps")
    
    # Define exclusion zone for right side
    exclusion_zone = {
        'x1': int(width * 0.75),  # Right 25%
        'y1': 0,
        'x2': width,
        'y2': int(height * 0.6)   # Upper 60%
    }
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    max_frames = fps * 5  # 5 seconds
    
    logger.info("Processing first 5 seconds...")
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process with improved parameters
        results = model(
            frame,
            conf=0.6,      # Higher confidence
            iou=0.5,       # NMS threshold
            max_det=50,    # Limit detections
            verbose=False
        )
        
        annotated_frame = frame.copy()
        
        # Draw exclusion zone for visualization
        cv2.rectangle(annotated_frame, 
                     (exclusion_zone['x1'], exclusion_zone['y1']), 
                     (exclusion_zone['x2'], exclusion_zone['y2']), 
                     (128, 128, 128), 2)
        cv2.putText(annotated_frame, "EXCLUSION ZONE", 
                   (exclusion_zone['x1'] + 10, exclusion_zone['y1'] + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
        
        if results[0].boxes is not None and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                if cls in model.names:
                    label = model.names[cls]
                else:
                    label = f"class_{cls}"
                
                # Check if in exclusion zone
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                in_exclusion = (exclusion_zone['x1'] <= center_x <= exclusion_zone['x2'] and 
                               exclusion_zone['y1'] <= center_y <= exclusion_zone['y2'])
                
                if in_exclusion:
                    # Draw filtered detection in red
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
                    cv2.putText(annotated_frame, f"FILTERED: {label}", 
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                    continue
                
                # Size filtering
                box_width = x2 - x1
                box_height = y2 - y1
                box_area = box_width * box_height
                frame_area = width * height
                relative_area = box_area / frame_area
                
                if relative_area > 0.4 or relative_area < 0.001:
                    # Draw size-filtered detection in orange
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 165, 255), 1)
                    cv2.putText(annotated_frame, f"SIZE FILTERED: {label}", 
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
                    continue
                
                # Draw valid detection in green
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"{label} {conf:.2f}", 
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        out.write(annotated_frame)
        frame_count += 1
        
        if frame_count % 30 == 0:
            logger.info(f"Processed {frame_count}/{max_frames} frames")
    
    cap.release()
    out.release()
    
    logger.info(f"Test video saved to: {output_path}")
    logger.info("Green boxes: Valid detections")
    logger.info("Red boxes: Filtered by exclusion zone")
    logger.info("Orange boxes: Filtered by size")

if __name__ == "__main__":
    quick_test()