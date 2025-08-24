#!/bin/bash

# Script to create GitHub Release with video assets for UMDL2
# This eliminates the need for a backend server by hosting videos on GitHub

set -e

# Configuration
REPO="AI-Mobility-Research-Lab/UMDL2"
VERSION="v1.0.0"
TITLE="UMDL2 Video Assets ${VERSION}"
NOTES="Video files for Urban Mobility Data Living Laboratory traffic monitoring demos

## Included Files
- 3 Processed videos with virtual loop overlays
- 3 Original videos
- Total size: ~1.4 GB

## Usage
Videos are served via jsDelivr CDN:
\`\`\`
https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/[filename]
\`\`\`
"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Creating GitHub Release for UMDL2 Videos${NC}"
echo -e "Repository: ${YELLOW}${REPO}${NC}"
echo -e "Version: ${YELLOW}${VERSION}${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) is not installed${NC}"
    echo "Install it with: sudo apt install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated with GitHub${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Video files to upload
PROCESSED_VIDEOS=(
    "processed_videos/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4"
    "processed_videos/Amsterdam-80th_adjusted_loop_full_demo.mp4"
    "processed_videos/Columbus-86th_adjusted_loop_full_demo.mp4"
)

ORIGINAL_VIDEOS=(
    "videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4"
    "videos/Amsterdam-80th_2025-02-13_06-00-04.mp4"
    "videos/Columbus-86th_2025-02-13_06-00-06.mp4"
)

# Check if all files exist
echo -e "${YELLOW}📋 Checking video files...${NC}"
for video in "${PROCESSED_VIDEOS[@]}" "${ORIGINAL_VIDEOS[@]}"; do
    if [ ! -f "$video" ]; then
        echo -e "${RED}❌ Missing file: $video${NC}"
        exit 1
    else
        size=$(du -h "$video" | cut -f1)
        echo -e "  ✅ $video (${size})"
    fi
done

# Calculate total size
TOTAL_SIZE=$(du -ch "${PROCESSED_VIDEOS[@]}" "${ORIGINAL_VIDEOS[@]}" | grep total | cut -f1)
echo -e "${GREEN}📦 Total size: ${TOTAL_SIZE}${NC}"
echo ""

# Check if release already exists
if gh release view "$VERSION" --repo "$REPO" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Release ${VERSION} already exists${NC}"
    read -p "Do you want to delete it and create a new one? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deleting existing release...${NC}"
        gh release delete "$VERSION" --repo "$REPO" --yes
    else
        echo "Aborted."
        exit 1
    fi
fi

# Create the release
echo -e "${GREEN}📤 Creating release and uploading videos...${NC}"
echo "This may take several minutes depending on your internet speed..."
echo ""

gh release create "$VERSION" \
    "${PROCESSED_VIDEOS[@]}" \
    "${ORIGINAL_VIDEOS[@]}" \
    --repo "$REPO" \
    --title "$TITLE" \
    --notes "$NOTES" \
    --latest

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Release created successfully!${NC}"
    echo ""
    echo -e "${GREEN}📺 Video URLs via jsDelivr CDN:${NC}"
    echo ""
    echo "Processed videos:"
    for video in "${PROCESSED_VIDEOS[@]}"; do
        filename=$(basename "$video")
        echo "  https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/${filename}"
    done
    echo ""
    echo "Original videos:"
    for video in "${ORIGINAL_VIDEOS[@]}"; do
        filename=$(basename "$video")
        echo "  https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/${filename}"
    done
    echo ""
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "1. Update src/config/cdn.ts with version: ${VERSION}"
    echo "2. Copy JSON files to public/data/"
    echo "3. Build and deploy frontend"
    echo "4. Test video playback"
else
    echo -e "${RED}❌ Failed to create release${NC}"
    exit 1
fi