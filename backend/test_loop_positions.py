#!/usr/bin/env python3
"""
Test script for updated loop positions in Amsterdam-80th and Columbus-86th
"""

import os
import sys
from pathlib import Path
from video_processor_with_loops import VideoProcessorWithLoops
from loop_configs import get_loop_config

def test_location(location_id: str, video_filename: str):
    """Test a specific location with updated loop configuration"""
    
    print(f"\n🎬 Testing {location_id}")
    print(f"📹 Video: {video_filename}")
    
    # Show current loop configuration
    loop_config = get_loop_config(location_id)
    if loop_config:
        for loop in loop_config:
            points = loop['zone_points']
            print(f"🔄 Loop '{loop['name']}': {points[0]} to {points[2]}")
    
    # Model path
    model_path = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"
    input_video = f"videos/{video_filename}"
    
    # Check if video exists
    if not Path(input_video).exists():
        print(f"❌ Video not found: {input_video}")
        return False
    
    # Output paths
    output_video = f"processed_videos/{location_id}_loop_position_test.mp4"
    output_json = f"processed_videos/{location_id}_loop_position_test.json"
    
    try:
        # Initialize processor
        processor = VideoProcessorWithLoops(model_path, location_id)
        
        # Process video
        print("🚀 Processing video...")
        success = processor.process_video_with_loops(
            input_video,
            output_video,
            output_json,
            conf_threshold=0.6
        )
        
        if success:
            print(f"✅ Success! Output: {output_video}")
            
            # Check if count data exists
            if Path(output_json).exists():
                import json
                with open(output_json, 'r') as f:
                    data = json.load(f)
                    total_count = data.get('total_vehicles', 0)
                    print(f"🚗 Total vehicle count: {total_count}")
            
            return True
        else:
            print("❌ Processing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 Testing updated loop positions")
    
    # Test locations with their respective videos
    test_cases = [
        ("Amsterdam-80th", "Amsterdam-80th_2025-02-13_06-00-04.mp4"),
        ("Columbus-86th", "Columbus-86th_2025-02-13_06-00-06.mp4")
    ]
    
    results = {}
    
    for location_id, video_filename in test_cases:
        results[location_id] = test_location(location_id, video_filename)
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    for location_id, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL" 
        print(f"   {location_id}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)