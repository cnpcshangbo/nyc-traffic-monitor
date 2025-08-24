#!/usr/bin/env python3
"""
Test virtual loop counting with visible tracking IDs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_tracking_ids():
    """Test YOLO tracking with visible tracking IDs on each frame"""
    
    # Use existing test video
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    output_video = "processed_videos/tracking_ids_demo.mp4"
    output_json = "processed_videos/tracking_ids_demo.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("Testing YOLO tracking with visible tracking IDs...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ Tracking IDs demo completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Tracking IDs demo video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/tracking_ids_demo.mp4")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show some JSON content
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"\n📊 Tracking IDs demo results:")
                logger.info(f"  Virtual loops: {len(data.get('virtual_loops', {}))}")
                for loop_name, loop_data in data.get('virtual_loops', {}).items():
                    logger.info(f"    - {loop_name}: {loop_data['total_count']} vehicles")
                    if loop_data.get('vehicle_counts'):
                        for vehicle_type, count in loop_data['vehicle_counts'].items():
                            logger.info(f"      • {vehicle_type}: {count}")
                logger.info(f"  Total crossings: {data.get('total_crossings', 0)}")
                
                # Show tracking details from crossings
                if 'time_series' in data and data['time_series']:
                    logger.info(f"\n🔍 Tracking details from crossings:")
                    for interval in data['time_series']:
                        for crossing in interval.get('crossings', []):
                            logger.info(f"    Vehicle ID {crossing['vehicle_id']} ({crossing['class_name']}) "
                                      f"crossed at frame {crossing.get('frame_number', 'unknown')}")
            
            return True
        else:
            logger.error("❌ Tracking IDs demo failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_tracking_ids()
    if success:
        logger.info("\n🎯 Tracking IDs demo features:")
        logger.info("  • Each bounding box shows 'ID:X ClassName: confidence'")
        logger.info("  • Tracking IDs persist across frames (ID 2, ID 10, etc.)")
        logger.info("  • Shows how YOLO maintains consistent vehicle identities")
        logger.info("  • Visual proof that each vehicle gets unique tracking ID")
        logger.info("  • Cyan loop displays live accurate count with ID tracking")
        logger.info("\n🚦 Perfect for understanding how tracking prevents duplicates!")
    
    sys.exit(0 if success else 1)