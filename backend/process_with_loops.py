#!/usr/bin/env python3
"""
Process videos with virtual inductive loop system
Generates both processed video with overlays and traffic volume JSON data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import argparse
from pathlib import Path
from typing import Dict
from video_processor_with_loops import VideoProcessorWithLoops

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MODEL_PATH = "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt"

def process_location_video(location_id: str, input_video_path: str, 
                          output_dir: str = "processed_videos", 
                          conf_threshold: float = 0.6) -> bool:
    """
    Process a single location video with virtual loops
    
    Args:
        location_id: Location identifier (e.g., "74th-Amsterdam-Columbus")
        input_video_path: Path to input video file
        output_dir: Directory to save output files
        conf_threshold: Detection confidence threshold
        
    Returns:
        True if processing successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output paths
        input_name = Path(input_video_path).stem
        output_video_path = os.path.join(output_dir, f"{input_name}_with_loops.mp4")
        output_json_path = os.path.join(output_dir, f"{input_name}_traffic_data.json")
        
        logger.info(f"Processing {location_id}: {input_video_path}")
        logger.info(f"Output video: {output_video_path}")
        logger.info(f"Output data: {output_json_path}")
        
        # Initialize processor
        processor = VideoProcessorWithLoops(MODEL_PATH, location_id)
        
        # Process video
        success = processor.process_video_with_loops(
            input_video_path, 
            output_video_path, 
            output_json_path, 
            conf_threshold
        )
        
        if success:
            logger.info(f"✅ Successfully processed {location_id}")
            return True
        else:
            logger.error(f"❌ Failed to process {location_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error processing {location_id}: {e}")
        return False

def process_all_locations(input_dir: str = "videos", output_dir: str = "processed_videos",
                         conf_threshold: float = 0.6) -> Dict[str, bool]:
    """
    Process all location videos with virtual loops
    
    Args:
        input_dir: Directory containing input videos
        output_dir: Directory to save output files  
        conf_threshold: Detection confidence threshold
        
    Returns:
        Dictionary mapping location_id to processing success status
    """
    # Define video files for each location
    location_videos = {
        "74th-Amsterdam-Columbus": "74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4",
        "Amsterdam-80th": "Amsterdam-80th_2025-02-13_06-00-04.mp4", 
        "Columbus-86th": "Columbus-86th_2025-02-13_06-00-06.mp4"
    }
    
    results = {}
    
    for location_id, video_filename in location_videos.items():
        input_path = os.path.join(input_dir, video_filename)
        
        if not os.path.exists(input_path):
            logger.warning(f"Video not found: {input_path}")
            results[location_id] = False
            continue
            
        success = process_location_video(location_id, input_path, output_dir, conf_threshold)
        results[location_id] = success
        
        if success:
            logger.info(f"✅ {location_id}: Completed successfully")
        else:
            logger.error(f"❌ {location_id}: Processing failed")
    
    # Summary
    successful = sum(results.values())
    total = len(results)
    logger.info(f"\n=== PROCESSING SUMMARY ===")
    logger.info(f"Successful: {successful}/{total}")
    
    for location_id, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"  {status} {location_id}")
    
    return results

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Process videos with virtual inductive loops")
    parser.add_argument("--location", "-l", type=str, 
                       help="Process specific location (e.g., '74th-Amsterdam-Columbus')")
    parser.add_argument("--input", "-i", type=str,
                       help="Input video path (required if --location is specified)")
    parser.add_argument("--input-dir", type=str, default="videos",
                       help="Input directory for batch processing (default: videos)")
    parser.add_argument("--output-dir", "-o", type=str, default="processed_videos",
                       help="Output directory (default: processed_videos)")
    parser.add_argument("--conf-threshold", "-c", type=float, default=0.6,
                       help="Detection confidence threshold (default: 0.6)")
    parser.add_argument("--all", action="store_true",
                       help="Process all locations")
    
    args = parser.parse_args()
    
    if args.location and args.input:
        # Process single location
        success = process_location_video(args.location, args.input, args.output_dir, args.conf_threshold)
        sys.exit(0 if success else 1)
        
    elif args.all:
        # Process all locations
        results = process_all_locations(args.input_dir, args.output_dir, args.conf_threshold)
        successful = sum(results.values())
        sys.exit(0 if successful == len(results) else 1)
        
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Process single location")
        print("  python process_with_loops.py -l 74th-Amsterdam-Columbus -i videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4")
        print("  # Process all locations")
        print("  python process_with_loops.py --all")
        sys.exit(1)

if __name__ == "__main__":
    main()