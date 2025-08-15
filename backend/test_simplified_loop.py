#!/usr/bin/env python3
"""
Test simplified single virtual loop with real-time traffic counter display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_simplified_loop_with_counter():
    """Test simplified single loop with real-time traffic counter overlay"""
    
    # Use existing test video
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    output_video = "processed_videos/simplified_loop_counter.mp4"
    output_json = "processed_videos/simplified_loop_counter.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("Testing simplified single loop with real-time traffic counter...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ Simplified loop with counter test completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Simplified video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/simplified_loop_counter.mp4")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show some JSON content
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"\nSimplified traffic counting summary:")
                logger.info(f"  Virtual loops: {len(data.get('virtual_loops', {}))}")
                for loop_name, loop_data in data.get('virtual_loops', {}).items():
                    logger.info(f"    - {loop_name}: {loop_data['total_count']} vehicles")
                    if loop_data.get('vehicle_counts'):
                        for vehicle_type, count in loop_data['vehicle_counts'].items():
                            logger.info(f"      • {vehicle_type}: {count}")
                logger.info(f"  Total crossings: {data.get('total_crossings', 0)}")
            
            return True
        else:
            logger.error("❌ Simplified loop test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_simplified_loop_with_counter()
    if success:
        logger.info("\n🎯 Simplified traffic counting features:")
        logger.info("  • Single cyan detection zone (Side Street Traffic)")
        logger.info("  • Real-time traffic counter displayed on video")
        logger.info("  • Live vehicle breakdown (PC, Truck, etc.)")
        logger.info("  • No complex JSON charts needed - everything on video!")
        logger.info("\n🚦 Much simpler and more intuitive for demos!")
    
    sys.exit(0 if success else 1)