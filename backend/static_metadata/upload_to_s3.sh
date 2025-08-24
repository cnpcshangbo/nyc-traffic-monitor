#!/bin/bash
# S3 Upload Script for UMDL2 Static Assets
# Usage: ./upload_to_s3.sh <bucket-name>

BUCKET_NAME=${1:-umdl2-static}

echo "🚀 Uploading to S3 bucket: $BUCKET_NAME"

# Create bucket if it doesn't exist
aws s3 mb s3://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Upload processed videos
echo "📹 Uploading processed videos..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/videos/processed/ \
  --exclude "*.json" \
  --exclude "*.jpg" \
  --content-type "video/mp4" \
  --acl public-read

# Upload original videos
echo "📹 Uploading original videos..."
for location in "74th-Amsterdam-Columbus" "Amsterdam-80th" "Columbus-86th"; do
  aws s3 sync videos/ s3://$BUCKET_NAME/videos/original/$location/ \
    --exclude "*" \
    --include "${location}_*.mp4" \
    --content-type "video/mp4" \
    --acl public-read
done

# Upload JSON data files
echo "📊 Uploading JSON data..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/data/live-traffic/ \
  --exclude "*" \
  --include "live_traffic_*.json" \
  --content-type "application/json" \
  --acl public-read

# Upload static metadata
echo "📄 Uploading metadata..."
aws s3 cp static_metadata/locations.json s3://$BUCKET_NAME/data/ \
  --content-type "application/json" \
  --acl public-read

# Upload verification images
echo "🖼️ Uploading images..."
aws s3 sync processed_videos/ s3://$BUCKET_NAME/images/ \
  --exclude "*" \
  --include "*.jpg" \
  --content-type "image/jpeg" \
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
