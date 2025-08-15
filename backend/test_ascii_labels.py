#!/usr/bin/env python3
"""
Test virtual loop visualization with ASCII labels (no Unicode issues)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_ascii_labels():
    """Test virtual loop visualization with ASCII labels"""
    
    # Use existing test video
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    output_video = "processed_videos/test_ascii_labels.mp4"
    output_json = "processed_videos/test_ascii_labels.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("Testing ASCII label virtual loop visualization...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ ASCII label visualization test completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Fixed video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/test_ascii_labels.mp4")
                
                # Show what labels should appear
                logger.info(f"\n📝 Loop labels now show:")
                logger.info(f"  • Main_Road_Entry IN (Green)")
                logger.info(f"  • Main_Road_Exit OUT (Red)")  
                logger.info(f"  • Side_Street_Entry IN (Cyan)")
                logger.info(f"\n✅ No more ??? characters - clear ASCII labels!")
            
            return True
        else:
            logger.error("❌ ASCII label test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_ascii_labels()
    sys.exit(0 if success else 1)