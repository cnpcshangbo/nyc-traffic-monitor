#!/usr/bin/env python3
"""
Test script for Amsterdam-80th location with new bottom center loop position
"""

import os
import sys
from pathlib import Path
from video_processor_with_loops import VideoProcessorWithLoops

def main():
    # Configuration
    model_path = Path("/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt")
    location_id = "Amsterdam-80th"
    input_video = "videos/Amsterdam-80th_2025-02-13_06-00-04.mp4"
    
    print(f"🎬 Testing {location_id} with bottom center loop position")
    print(f"📹 Input video: {input_video}")
    
    # Check if input video exists
    if not Path(input_video).exists():
        print(f"❌ Input video not found: {input_video}")
        return False
    
    # Initialize processor
    try:
        processor = VideoProcessorWithLoops(model_path, location_id)
        print("✅ Video processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return False
    
    # Process short test video (30 seconds)
    try:
        print("🚀 Starting video processing (30 seconds)...")
        result = processor.process_video_with_loops(
            input_video,
            start_time=60,  # Start at 1 minute
            duration=30,    # Process 30 seconds
            output_suffix='_bottom_center_test'
        )
        
        if result and result.get('success'):
            output_path = result.get('output_path')
            count_data = result.get('count_data', {})
            
            print(f"✅ Processing completed successfully!")
            print(f"📁 Output video: {output_path}")
            print(f"🚗 Vehicle counts: {count_data}")
            
            # Show counts per loop
            for loop_name, count in count_data.items():
                print(f"   {loop_name}: {count} vehicles")
            
            return True
        else:
            print(f"❌ Processing failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)