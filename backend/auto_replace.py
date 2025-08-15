#!/usr/bin/env python3
"""
Script to automatically replace the 5-second video with the full improved video when ready
"""

import os
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_and_replace():
    """Monitor for the completion of full video processing and replace"""
    
    improved_video = Path("processed_videos/Columbus-86th_2025-02-13_06-00-06_improved.mp4")
    current_video = Path("processed_videos/Columbus-86th_2025-02-13_06-00-06_processed.mp4")
    backup_video = Path("processed_videos/Columbus-86th_2025-02-13_06-00-06_processed_backup.mp4")
    
    logger.info("Monitoring for completion of full video processing...")
    logger.info(f"Waiting for: {improved_video}")
    
    while True:
        if improved_video.exists():
            logger.info("Full improved video found! Replacing...")
            
            # Replace the current 5-second video with the full improved video
            if current_video.exists():
                # Keep the 5-second as a backup too
                temp_backup = Path("processed_videos/Columbus-86th_5sec_backup.mp4")
                current_video.rename(temp_backup)
                logger.info(f"Backed up 5-second video to: {temp_backup}")
            
            # Move the improved video to the current position
            improved_video.rename(current_video)
            logger.info(f"Replaced with full improved video: {current_video}")
            
            # Check file size to confirm
            file_size = current_video.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"New video size: {file_size:.1f} MB")
            
            break
        
        # Check every 30 seconds
        time.sleep(30)
    
    logger.info("Auto-replacement completed successfully!")

if __name__ == "__main__":
    monitor_and_replace()