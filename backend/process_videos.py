#!/usr/bin/env python3
"""
Script to process all three intersection videos with YOLOv8
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.video_processor import VideoProcessor
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def main():
    """Process all three intersection videos"""
    
    processor = VideoProcessor(MODEL_PATH)
    
    videos = [
        {
            "location": "74th-Amsterdam-Columbus",
            "filename": "2025-02-13_06-00-04.mp4"
        },
        {
            "location": "Amsterdam-80th", 
            "filename": "2025-02-13_06-00-04.mp4"
        },
        {
            "location": "Columbus-86th",
            "filename": "2025-02-13_06-00-06.mp4"
        }
    ]
    
    processed_dir = Path("processed_videos")
    processed_dir.mkdir(exist_ok=True)
    
    for video in videos:
        input_path = f"../public/{video['location']}/{video['filename']}"
        output_filename = f"{video['location']}_{video['filename'].replace('.mp4', '_processed.mp4')}"
        output_path = processed_dir / output_filename
        
        if not os.path.exists(input_path):
            logger.error(f"Video not found: {input_path}")
            continue
        
        if output_path.exists():
            logger.info(f"Already processed: {output_path}")
            continue
        
        try:
            logger.info(f"Processing {video['location']}...")
            processor.process_video(input_path, str(output_path), conf_threshold=0.3)
            logger.info(f"Successfully processed {video['location']}")
        except Exception as e:
            logger.error(f"Failed to process {video['location']}: {e}")

if __name__ == "__main__":
    main()