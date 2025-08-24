#!/usr/bin/env python3
"""
Generate demo videos with updated loop positions for Amsterdam-80th and Columbus-86th
"""

import subprocess
import sys
from pathlib import Path

def generate_demo(location_id: str, video_filename: str, start_time: int = 60, duration: int = 30):
    """Generate a short demo video with updated loop positions"""
    
    print(f"🎬 Generating demo for {location_id}")
    
    # Input and output paths
    input_video = f"videos/{video_filename}"
    output_video = f"processed_videos/{location_id}_updated_loop_demo.mp4"
    output_json = f"processed_videos/{location_id}_updated_loop_demo.json"
    
    if not Path(input_video).exists():
        print(f"❌ Input video not found: {input_video}")
        return False
    
    # Use FFmpeg to extract a short segment first
    temp_video = f"temp_{location_id}_segment.mp4"
    
    print(f"📹 Extracting {duration}s segment from {start_time}s...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+faststart",
        temp_video
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"✅ Segment extracted: {temp_video}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed: {e}")
        return False
    
    # Process the segment with virtual loops
    print("🚀 Processing with virtual loops...")
    
    process_cmd = [
        "python", "-c", f"""
import sys
sys.path.append('.')
from video_processor_with_loops import VideoProcessorWithLoops

try:
    processor = VideoProcessorWithLoops(
        '/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt',
        '{location_id}'
    )
    
    success = processor.process_video_with_loops(
        '{temp_video}',
        '{output_video}',
        '{output_json}',
        conf_threshold=0.6
    )
    
    if success:
        print('✅ Processing completed successfully')
    else:
        print('❌ Processing failed')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ Error: {{e}}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    ]
    
    try:
        result = subprocess.run(process_cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        # Clean up temp file
        Path(temp_video).unlink(missing_ok=True)
        
        # Check if output exists
        if Path(output_video).exists():
            print(f"✅ Demo generated: {output_video}")
            return True
        else:
            print("❌ Output video not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Processing failed: {e}")
        print(f"Stderr: {e.stderr}")
        # Clean up temp file
        Path(temp_video).unlink(missing_ok=True)
        return False

def main():
    print("🎥 Generating updated loop position demos\n")
    
    demos = [
        ("Amsterdam-80th", "Amsterdam-80th_2025-02-13_06-00-04.mp4", 120, 45),  # 45s from 2min
        ("Columbus-86th", "Columbus-86th_2025-02-13_06-00-06.mp4", 60, 30)     # 30s from 1min
    ]
    
    results = []
    
    for location_id, video_filename, start_time, duration in demos:
        success = generate_demo(location_id, video_filename, start_time, duration)
        results.append((location_id, success))
        print()  # Add spacing
    
    # Summary
    print("📊 Generation Summary:")
    all_success = True
    for location_id, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {location_id}: {status}")
        if not success:
            all_success = False
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)