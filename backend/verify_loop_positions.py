#!/usr/bin/env python3
"""
Quick verification of loop positions without full video processing
"""

import cv2
import numpy as np
from pathlib import Path
from loop_configs import get_loop_config

def verify_location(location_id: str, video_filename: str):
    """Verify loop position on a single frame"""
    
    print(f"\n🎬 Verifying {location_id}")
    
    # Get loop configuration
    loop_config = get_loop_config(location_id)
    if not loop_config:
        print(f"❌ No loop configuration found for {location_id}")
        return False
    
    # Video path
    video_path = f"videos/{video_filename}"
    if not Path(video_path).exists():
        print(f"❌ Video not found: {video_path}")
        return False
    
    # Open video and get a frame
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return False
    
    # Seek to middle of video for better frame
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Cannot read frame from video")
        return False
    
    height, width = frame.shape[:2]
    print(f"📏 Video dimensions: {width}x{height}")
    
    # Draw loops on frame
    for loop in loop_config:
        name = loop['name']
        points = np.array(loop['zone_points'], dtype=np.int32)
        direction = loop['direction']
        
        print(f"🔄 Loop '{name}' ({direction}): {points.tolist()}")
        
        # Check if points are within frame bounds
        valid_points = True
        for point in points:
            x, y = point
            if x < 0 or x >= width or y < 0 or y >= height:
                print(f"⚠️  Point ({x}, {y}) is outside frame bounds!")
                valid_points = False
        
        if valid_points:
            print("✅ All points are within frame bounds")
        
        # Draw semi-transparent filled polygon
        overlay = frame.copy()
        cv2.fillPoly(overlay, [points], (0, 255, 0))  # Green fill
        cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
        
        # Draw border
        cv2.polylines(frame, [points], True, (0, 255, 0), 2)
        
        # Add label
        center_x = int(np.mean(points[:, 0]))
        center_y = int(np.mean(points[:, 1]))
        cv2.putText(frame, f"{name}", (center_x-40, center_y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, direction.upper(), (center_x-20, center_y+15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Save verification image
    output_image = f"processed_videos/{location_id}_loop_verification.jpg"
    cv2.imwrite(output_image, frame)
    print(f"💾 Verification image saved: {output_image}")
    
    return True

def main():
    print("🔍 Verifying updated loop positions")
    
    locations = [
        ("Amsterdam-80th", "Amsterdam-80th_2025-02-13_06-00-04.mp4"),
        ("Columbus-86th", "Columbus-86th_2025-02-13_06-00-06.mp4")
    ]
    
    all_success = True
    
    for location_id, video_filename in locations:
        success = verify_location(location_id, video_filename)
        if not success:
            all_success = False
    
    print(f"\n📊 Verification Summary: {'✅ ALL GOOD' if all_success else '❌ ISSUES FOUND'}")
    return all_success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)