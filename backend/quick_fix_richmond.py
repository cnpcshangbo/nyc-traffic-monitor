#!/usr/bin/env python3
"""
Quick fix for Richmond Hill Road traffic light false detection
Create a shorter test video first to verify the fix works
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

def create_test_video():
    """Create a 10-second test video to verify the fix"""
    
    input_video = "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    output_video = "processed_videos/74th-Amsterdam-Columbus_test_10sec_fixed.mp4"
    
    if not os.path.exists(input_video):
        logger.error(f"Video not found: {input_video}")
        return False
    
    # Load model
    logger.info("Loading YOLO model...")
    model = YOLO(MODEL_PATH)
    
    cap = cv2.VideoCapture(input_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    logger.info(f"Video: {width}x{height}, {fps}fps")
    
    # Define exclusion zone for traffic light at (1816, 447)
    exclusion_zone = {
        'x1': 1715,
        'y1': 347, 
        'x2': 1915,
        'y2': 547
    }
    logger.info(f"Exclusion zone: {exclusion_zone}")
    
    # Create temp video with OpenCV
    import tempfile
    temp_dir = tempfile.mkdtemp()
    temp_video = os.path.join(temp_dir, "temp.avi")
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    frame_count = 0
    max_frames = fps * 10  # 10 seconds
    
    def is_in_exclusion_zone(bbox, zone):
        """Check if detection center is in exclusion zone"""
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return (zone['x1'] <= center_x <= zone['x2'] and 
                zone['y1'] <= center_y <= zone['y2'])
    
    def is_valid_detection(bbox, conf, class_name):
        """Enhanced validation for detections"""
        x1, y1, x2, y2 = bbox
        det_width = x2 - x1
        det_height = y2 - y1
        
        # Basic size check
        if det_width < 10 or det_height < 10:
            return False
            
        # Check exclusion zone
        if is_in_exclusion_zone(bbox, exclusion_zone):
            logger.debug(f"Rejected {class_name} in exclusion zone")
            return False
            
        # Enhanced filtering for Bk/Mc
        if 'bk' in class_name.lower() or 'mc' in class_name.lower():
            # Higher confidence threshold
            if conf < 0.7:
                logger.debug(f"Rejected {class_name}: low confidence {conf:.2f}")
                return False
                
            # Reject small vertical objects (likely traffic lights)
            aspect_ratio = det_width / det_height if det_height > 0 else 0
            if aspect_ratio < 0.4:  # Very vertical
                logger.debug(f"Rejected {class_name}: vertical aspect {aspect_ratio:.2f}")
                return False
                
            # Reject very small objects
            if det_width < 40 or det_height < 40:
                logger.debug(f"Rejected {class_name}: too small {det_width}x{det_height}")
                return False
                
        return True
    
    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Run detection
        results = model(frame, conf=0.5, verbose=False)
        
        # Draw exclusion zone for visualization
        cv2.rectangle(frame, (exclusion_zone['x1'], exclusion_zone['y1']), 
                     (exclusion_zone['x2'], exclusion_zone['y2']), (0, 0, 255), 2)
        cv2.putText(frame, "EXCLUSION ZONE", (exclusion_zone['x1'], exclusion_zone['y1']-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Process detections
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
                    
                    # Apply validation
                    if not is_valid_detection(bbox, conf, class_name):
                        continue
                    
                    # Draw valid detections
                    x1, y1, x2, y2 = bbox
                    
                    # Color by class
                    colors = {
                        'pc': (0, 255, 0),      # Green
                        'truck': (0, 0, 255),   # Red
                        'bus': (255, 0, 0),     # Blue
                        'bk/mc': (0, 255, 255), # Yellow
                        'ped': (255, 165, 0),   # Orange
                    }
                    color = colors.get(class_name.lower(), (128, 128, 128))
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    label = f"{class_name}: {conf:.2f}"
                    cv2.putText(frame, label, (x1, y1-5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        out.write(frame)
        frame_count += 1
        
        if frame_count % (fps * 2) == 0:  # Every 2 seconds
            logger.info(f"Progress: {frame_count/max_frames*100:.1f}%")
    
    cap.release()
    out.release()
    
    # Convert to web-compatible MP4
    logger.info("Converting to MP4...")
    ffmpeg_cmd = [
        'ffmpeg', '-i', temp_video,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-movflags', '+faststart', '-y', output_video
    ]
    
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr}")
        return False
    
    # Cleanup
    os.unlink(temp_video)
    os.rmdir(temp_dir)
    
    logger.info(f"✅ Test video created: {output_video}")
    
    # Check file size
    if os.path.exists(output_video):
        file_size = os.path.getsize(output_video) / (1024 * 1024)
        logger.info(f"File size: {file_size:.1f} MB")
    
    return True

if __name__ == "__main__":
    success = create_test_video()
    if success:
        logger.info("✅ Quick fix test completed successfully!")
        logger.info("🔍 Check the test video to verify the traffic light is no longer detected")
    else:
        logger.error("❌ Quick fix failed")