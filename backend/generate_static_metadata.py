#!/usr/bin/env python3
"""
Generate static metadata files for S3 deployment
"""

import json
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
PROCESSED_VIDEOS_DIR = BASE_DIR / "processed_videos"
OUTPUT_DIR = BASE_DIR / "static_metadata"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

def generate_locations_json():
    """Generate static locations.json for S3"""
    
    locations = []
    
    # Define location metadata
    location_configs = [
        {
            "id": "74th-Amsterdam-Columbus",
            "name": "Richmond Hill Road & Edinboro Rd, Staten Island",
            "original_video": "2025-02-13_06-00-04.mp4",
            "coordinates": [40.5372, -74.2435]  # Staten Island coordinates
        },
        {
            "id": "Amsterdam-80th",
            "name": "Arthur Kill Rd & Storer Ave, Staten Island",
            "original_video": "2025-02-13_06-00-04.mp4",
            "coordinates": [40.5784, -74.2367]  # Staten Island coordinates
        },
        {
            "id": "Columbus-86th",
            "name": "Katonah Ave & East 241st St, Bronx",
            "original_video": "2025-02-13_06-00-06.mp4",
            "coordinates": [40.8931, -73.8675]  # Bronx coordinates
        }
    ]
    
    # Check for processed videos for each location
    for config in location_configs:
        location_id = config["id"]
        
        # Find processed videos
        processed_files = []
        
        # Priority order for demo videos
        demo_patterns = [
            f"{location_id}_adjusted_loop_full_demo.mp4",
            f"{location_id}_*_processed.mp4",
        ]
        
        for pattern in demo_patterns:
            for file in PROCESSED_VIDEOS_DIR.glob(pattern):
                if file.name not in processed_files:
                    processed_files.append(file.name)
        
        # Add general demo videos for first location
        if location_id == "74th-Amsterdam-Columbus":
            for file in ["live_traffic_demo.mp4", "tracking_ids_demo.mp4", "adjusted_loop_full_demo.mp4"]:
                if (PROCESSED_VIDEOS_DIR / file).exists() and file not in processed_files:
                    processed_files.append(file)
        
        location = {
            "id": location_id,
            "name": config["name"],
            "coordinates": config["coordinates"],
            "original_video": config["original_video"],
            "has_processed": len(processed_files) > 0,
            "processed_files": processed_files
        }
        
        locations.append(location)
    
    # Write locations.json
    output_file = OUTPUT_DIR / "locations.json"
    with open(output_file, 'w') as f:
        json.dump({"locations": locations}, f, indent=2)
    
    print(f"✅ Generated {output_file}")
    return locations

def generate_s3_upload_script():
    """Generate shell script for S3 upload"""
    
    script_content = """#!/bin/bash
# S3 Upload Script for UMDL2 Static Assets
# Usage: ./upload_to_s3.sh <bucket-name>

BUCKET_NAME=${1:-umdl2-static}

echo "🚀 Uploading to S3 bucket: $BUCKET_NAME"

# Create bucket if it doesn't exist
aws s3 mb s3://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Upload processed videos
echo "📹 Uploading processed videos..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/videos/processed/ \\
  --exclude "*.json" \\
  --exclude "*.jpg" \\
  --content-type "video/mp4" \\
  --acl public-read

# Upload original videos
echo "📹 Uploading original videos..."
for location in "74th-Amsterdam-Columbus" "Amsterdam-80th" "Columbus-86th"; do
  aws s3 sync videos/ s3://$BUCKET_NAME/videos/original/$location/ \\
    --exclude "*" \\
    --include "${location}_*.mp4" \\
    --content-type "video/mp4" \\
    --acl public-read
done

# Upload JSON data files
echo "📊 Uploading JSON data..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/data/live-traffic/ \\
  --exclude "*" \\
  --include "live_traffic_*.json" \\
  --content-type "application/json" \\
  --acl public-read

# Upload static metadata
echo "📄 Uploading metadata..."
aws s3 cp static_metadata/locations.json s3://$BUCKET_NAME/data/ \\
  --content-type "application/json" \\
  --acl public-read

# Upload verification images
echo "🖼️ Uploading images..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/images/ \\
  --exclude "*" \\
  --include "*.jpg" \\
  --content-type "image/jpeg" \\
  --acl public-read

# Configure CORS
echo "⚙️ Configuring CORS..."
cat > cors.json << EOF
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedOrigins": [
        "https://ai-mobility-research-lab.github.io",
        "https://cnpcshangbo.github.io",
        "https://asdfghjklzxcvbnm.aimobilitylab.xyz",
        "http://localhost:5173"
      ],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3600
    }
  ]
}
EOF

aws s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://cors.json

echo "✅ Upload complete!"
echo "🌐 Access your files at: https://$BUCKET_NAME.s3.amazonaws.com/"

# Test access
echo "🧪 Testing access..."
curl -I https://$BUCKET_NAME.s3.amazonaws.com/data/locations.json
"""
    
    script_file = OUTPUT_DIR / "upload_to_s3.sh"
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_file.chmod(0o755)
    
    print(f"✅ Generated {script_file}")

def main():
    print("🎯 Generating static metadata for S3 deployment\n")
    
    # Generate locations.json
    locations = generate_locations_json()
    
    # Print summary
    print(f"\n📊 Summary:")
    for loc in locations:
        print(f"  - {loc['name']}: {len(loc['processed_files'])} processed videos")
    
    # Generate upload script
    generate_s3_upload_script()
    
    print(f"\n✨ Static metadata ready in {OUTPUT_DIR}/")
    print("\n📝 Next steps:")
    print("1. Configure AWS credentials: aws configure")
    print("2. Run upload script: ./static_metadata/upload_to_s3.sh <bucket-name>")
    print("3. Update frontend S3_BASE_URL in src/config/s3.ts")
    print("4. Deploy frontend and test")

if __name__ == "__main__":
    main()