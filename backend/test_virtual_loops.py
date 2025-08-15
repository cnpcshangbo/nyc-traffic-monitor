#!/usr/bin/env python3
"""
Quick test of virtual loop system with a short video segment
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def create_test_video_segment():
    """Create a 30-second test segment from Richmond Hill Road video"""
    
    input_video = "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    output_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    
    if not os.path.exists(input_video):
        logger.error(f"Input video not found: {input_video}")
        return False
        
    logger.info("Creating 30-second test video...")
    
    # Use FFmpeg to extract first 30 seconds
    import subprocess
    
    ffmpeg_cmd = [
        'ffmpeg', '-i', input_video,
        '-t', '30',  # Duration: 30 seconds
        '-c:v', 'libx264', '-c:a', 'copy',
        '-y', output_video
    ]
    
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr}")
        return False
        
    logger.info(f"✅ Created test video: {output_video}")
    return True

def test_virtual_loops():
    """Test virtual loop processing with short video"""
    
    # Create test video if it doesn't exist
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    if not os.path.exists(test_video):
        if not create_test_video_segment():
            return False
    
    # Test processing
    location_id = "74th-Amsterdam-Columbus"
    output_video = "processed_videos/test_loops_30sec.mp4"
    output_json = "processed_videos/test_loops_30sec.json"
    
    logger.info("Testing virtual loop processing...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, location_id)
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ Virtual loop test completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Test video created: {video_size:.1f} MB")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show some JSON content
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"Traffic summary:")
                logger.info(f"  Total crossings: {data.get('total_crossings', 0)}")
                logger.info(f"  Virtual loops: {len(data.get('virtual_loops', {}))}")
                logger.info(f"  Time intervals: {len(data.get('time_series', []))}")
            
            return True
        else:
            logger.error("❌ Virtual loop test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_virtual_loops()
    sys.exit(0 if success else 1)