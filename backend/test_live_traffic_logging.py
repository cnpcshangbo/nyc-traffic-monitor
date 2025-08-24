#!/usr/bin/env python3
"""
Test real-time traffic logging with frontend display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_live_traffic_logging():
    """Test real-time traffic logging system with frontend integration"""
    
    # Use the 30-second test video for faster testing
    test_video = "videos/74th-Amsterdam-Columbus_test_30sec.mp4"
    output_video = "processed_videos/live_traffic_demo.mp4"
    output_json = "processed_videos/live_traffic_demo.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Test video not found: {test_video}")
        return False
    
    logger.info("Testing real-time traffic logging with frontend integration...")
    logger.info("🔄 This will generate live JSON data that the frontend can display")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        # Processing will generate live_traffic_74th-Amsterdam-Columbus.json in real-time
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.65
        )
        
        if success:
            logger.info("✅ Live traffic logging test completed successfully!")
            
            # Check outputs
            live_traffic_file = "processed_videos/live_traffic_74th-Amsterdam-Columbus.json"
            
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Demo video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/live_traffic_demo.mp4")
                
            if os.path.exists(live_traffic_file):
                json_size = os.path.getsize(live_traffic_file) / 1024
                logger.info(f"✅ Live traffic data created: {json_size:.1f} KB")
                logger.info(f"📊 API URL: http://classificationbackend.boshang.online/live-traffic/74th-Amsterdam-Columbus")
                
                # Show live traffic data summary
                import json
                with open(live_traffic_file, 'r') as f:
                    live_data = json.load(f)
                    
                logger.info(f"\n📊 Live traffic data summary:")
                logger.info(f"  Status: {live_data.get('status', 'unknown')}")
                logger.info(f"  Total vehicles: {live_data.get('total_vehicles', 0)}")
                logger.info(f"  Vehicle types: {live_data.get('vehicle_types', {})}")
                logger.info(f"  Vehicles per minute: {live_data.get('traffic_rate', {}).get('vehicles_per_minute', 0)}")
                logger.info(f"  Time intervals: {len(live_data.get('time_intervals', []))}")
                logger.info(f"  Recent detections: {len(live_data.get('recent_detections', []))}")
                
                if live_data.get('summary'):
                    summary = live_data['summary']
                    logger.info(f"\n📈 Processing summary:")
                    logger.info(f"  Processing time: {summary.get('total_processing_time_minutes', 0):.1f} minutes")
                    logger.info(f"  Average rate: {summary.get('average_vehicles_per_minute', 0):.2f} vehicles/minute")
                    logger.info(f"  Peak interval: {summary.get('peak_interval_count', 0)} vehicles")
            
            return True
        else:
            logger.error("❌ Live traffic logging test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_live_traffic_logging()
    if success:
        logger.info("\n🎯 Live traffic logging features:")
        logger.info("  • Real-time JSON updates during video processing")
        logger.info("  • 15-second interval aggregation for traffic patterns")
        logger.info("  • Vehicle type distribution tracking")
        logger.info("  • Recent detections with tracking IDs")
        logger.info("  • Traffic rate calculations (vehicles/minute)")
        logger.info("  • Frontend auto-refresh capabilities")
        logger.info("\n🌐 Frontend Integration:")
        logger.info("  • Visit https://asdfghjklzxcvbnm.aimobilitylab.xyz/")
        logger.info("  • Select '74th–Amsterdam–Columbus' location") 
        logger.info("  • View 'Live Traffic Distribution' chart")
        logger.info("  • See real-time traffic patterns and vehicle types")
        logger.info("\n🚦 Perfect for monitoring traffic distribution over time!")
    
    sys.exit(0 if success else 1)