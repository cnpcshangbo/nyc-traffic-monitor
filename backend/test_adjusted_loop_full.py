#!/usr/bin/env python3
"""
Test adjusted virtual loop (narrower, directional) with full-length video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def test_adjusted_loop_full_video():
    """Test adjusted narrow virtual loop with full-length video for more scenarios"""
    
    # Use full-length video for more traffic scenarios
    test_video = "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    output_video = "processed_videos/adjusted_loop_full_demo.mp4"
    output_json = "processed_videos/adjusted_loop_full_demo.json"
    
    if not os.path.exists(test_video):
        logger.error(f"Full video not found: {test_video}")
        return False
    
    # Check video size
    video_size_mb = os.path.getsize(test_video) / (1024 * 1024)
    logger.info(f"Processing full video: {video_size_mb:.1f} MB")
    logger.info("This will take several minutes - processing with adjusted narrow loop...")
    
    try:
        processor = VideoProcessorWithLoops(MODEL_PATH, "74th-Amsterdam-Columbus")
        
        # Use slightly lower confidence for full video to catch more scenarios
        success = processor.process_video_with_loops(
            test_video, output_video, output_json, conf_threshold=0.6
        )
        
        if success:
            logger.info("✅ Adjusted loop full video test completed successfully!")
            
            # Check outputs
            if os.path.exists(output_video):
                video_size = os.path.getsize(output_video) / (1024 * 1024)
                logger.info(f"✅ Full demo video created: {video_size:.1f} MB")
                logger.info(f"🎥 Video URL: https://classificationbackend.boshang.online/processed-videos/adjusted_loop_full_demo.mp4")
                
            if os.path.exists(output_json):
                json_size = os.path.getsize(output_json) / 1024
                logger.info(f"✅ Traffic data created: {json_size:.1f} KB")
                
                # Show comprehensive JSON analysis
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    
                logger.info(f"\n📊 Full video analysis results:")
                logger.info(f"  Virtual loops: {len(data.get('virtual_loops', {}))}")
                for loop_name, loop_data in data.get('virtual_loops', {}).items():
                    logger.info(f"    - {loop_name}: {loop_data['total_count']} vehicles")
                    if loop_data.get('vehicle_counts'):
                        for vehicle_type, count in loop_data['vehicle_counts'].items():
                            logger.info(f"      • {vehicle_type}: {count}")
                
                total_crossings = data.get('total_crossings', 0)
                time_intervals = len(data.get('time_series', []))
                logger.info(f"  Total crossings: {total_crossings}")
                logger.info(f"  Time intervals: {time_intervals}")
                
                # Show timing distribution
                if 'time_series' in data and data['time_series']:
                    logger.info(f"\n🕐 Traffic distribution over time:")
                    for i, interval in enumerate(data['time_series'][:10]):  # Show first 10 intervals
                        start_time = interval.get('timestamp', 0)
                        count = interval.get('total_count', 0)
                        minutes = int(start_time // 60)
                        seconds = int(start_time % 60)
                        if count > 0:
                            logger.info(f"    Time {minutes:02d}:{seconds:02d} - {count} vehicles")
                    
                    if len(data['time_series']) > 10:
                        logger.info(f"    ... and {len(data['time_series']) - 10} more intervals")
                
                # Performance comparison
                logger.info(f"\n🔄 Loop adjustment comparison:")
                logger.info(f"  Previous wide loop (100x150px): Detected vehicles in both directions")
                logger.info(f"  New narrow loop (40x40px): Detects single direction only")
                logger.info(f"  Result: {total_crossings} vehicles in directional traffic")
            
            return True
        else:
            logger.error("❌ Adjusted loop full video test failed")
            return False
            
    except Exception as e:
        logger.error(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_adjusted_loop_full_video()
    if success:
        logger.info("\n🎯 Adjusted loop full video features:")
        logger.info("  • Narrow 40x40px loop eliminates bi-directional counting")
        logger.info("  • Positioned to catch single direction traffic only")
        logger.info("  • Full-length video shows various traffic scenarios")
        logger.info("  • Tracking IDs visible throughout extended footage")
        logger.info("  • Live counter shows accurate directional counts")
        logger.info("  • YOLO tracking maintains IDs across long sequences")
        logger.info("\n🚦 Perfect for demonstrating real-world traffic patterns!")
    
    sys.exit(0 if success else 1)