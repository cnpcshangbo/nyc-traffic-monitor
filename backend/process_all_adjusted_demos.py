#!/usr/bin/env python3
"""
Process adjusted loop full demo videos for all three locations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def process_location_demo(location_id: str, video_file: str):
    """Process adjusted loop full demo for a specific location"""
    
    test_video = f"videos/{video_file}"
    output_video = f"processed_videos/{location_id}_adjusted_loop_full_demo.mp4"
    output_json = f"processed_videos/{location_id}_adjusted_loop_full_demo.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Video not found: {test_video}")
        return False
    
    # Check video size
    video_size_mb = os.path.getsize(test_video) / (1024 * 1024)
    logger.info(f"Processing {location_id} full video: {video_size_mb:.1f} MB")
    logger.info("This will take several minutes with adjusted narrow loop...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, location_id)
        
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.6
        )
        
        if success:
            logger.info(f"✅ {location_id} adjusted loop demo completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Demo video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/{location_id}_adjusted_loop_full_demo.mp4")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show traffic data summary
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"\n📊 {location_id} traffic analysis:")
                for loop_name, loop_data in data.get('virtual_loops', {}).items():
                    logger.info(f"    - {loop_name}: {loop_data['total_count']} vehicles")
                    if loop_data.get('vehicle_counts'):
                        for vehicle_type, count in loop_data['vehicle_counts'].items():
                            logger.info(f"      • {vehicle_type}: {count}")
                logger.info(f"  Total crossings: {data.get('total_crossings', 0)}")
                logger.info(f"  Time intervals: {len(data.get('time_series', []))}")
            
            return True
        else:
            logger.error(f"❌ {location_id} demo processing failed")
            return False
            
    except Exception as e:
        logger.error(f"{location_id} processing error: {e}")
        return False

def main():
    """Process all three locations"""
    
    locations = [
        ("74th-Amsterdam-Columbus", "74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"),
        ("Amsterdam-80th", "Amsterdam-80th_2025-02-13_06-00-04.mp4"),
        ("Columbus-86th", "Columbus-86th_2025-02-13_06-00-06.mp4")
    ]
    
    logger.info("🚀 Starting adjusted loop demo processing for all locations...")
    logger.info("⏱️  This will process 3 full-length videos - estimated total time: 30-40 minutes")
    
    results = {}
    
    for location_id, video_file in locations:
        logger.info(f"\n🎯 Processing {location_id}...")
        results[location_id] = process_location_demo(location_id, video_file)
    
    # Summary
    logger.info("\n📋 Processing Summary:")
    successful = sum(1 for success in results.values() if success)
    
    for location_id, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        logger.info(f"  {location_id}: {status}")
    
    logger.info(f"\n🏁 Completed: {successful}/{len(locations)} locations processed successfully")
    
    if successful == len(locations):
        logger.info("\n🎯 All locations now have adjusted loop full demo videos:")
        for location_id, _ in locations:
            logger.info(f"  • {location_id}_adjusted_loop_full_demo.mp4")
        logger.info("\n🌐 Frontend will automatically use these videos when available!")
    
    return successful == len(locations)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)