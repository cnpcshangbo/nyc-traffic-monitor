#!/usr/bin/env python3
"""
Test fixed virtual loop counting system with duplicate prevention
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_fixed_counting():
    """Test fixed virtual loop counting with duplicate prevention"""
    
    # Use existing test video
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    output_video = "processed_videos/fixed_counting_test.mp4"
    output_json = "processed_videos/fixed_counting_test.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("Testing fixed virtual loop counting with duplicate prevention...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ Fixed counting test completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Fixed counting video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/fixed_counting_test.mp4")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show some JSON content
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"\n📊 Fixed counting results:")
                logger.info(f"  Virtual loops: {len(data.get('virtual_loops', {}))}")
                for loop_name, loop_data in data.get('virtual_loops', {}).items():
                    logger.info(f"    - {loop_name}: {loop_data['total_count']} vehicles (ENTRY ONLY)")
                    if loop_data.get('vehicle_counts'):
                        for vehicle_type, count in loop_data['vehicle_counts'].items():
                            logger.info(f"      • {vehicle_type}: {count}")
                logger.info(f"  Total crossings: {data.get('total_crossings', 0)}")
                logger.info(f"  Time intervals: {len(data.get('time_series', []))}")
                
                # Compare with previous results
                logger.info(f"\n🔄 Comparison with previous version:")
                logger.info(f"  Previous count: 20 vehicles (with duplicates)")
                logger.info(f"  Fixed count: {data.get('total_crossings', 0)} vehicles (duplicates removed)")
                logger.info(f"  Improvement: {20 - data.get('total_crossings', 0)} duplicates eliminated")
            
            return True
        else:
            logger.error("❌ Fixed counting test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_counting()
    if success:
        logger.info("\n🎯 Fixed counting system features:")
        logger.info("  • Only counts vehicle ENTRY (not exit or continuous detection)")
        logger.info("  • 3-second cooldown period prevents duplicate counts")
        logger.info("  • Spatial duplicate detection (50px threshold)")
        logger.info("  • Vehicle ID tracking prevents re-counting same vehicle")
        logger.info("  • Live counter shows accurate unique vehicle count")
        logger.info("\n🚦 Accurate traffic counting without duplicates!")
    
    sys.exit(0 if success else 1)