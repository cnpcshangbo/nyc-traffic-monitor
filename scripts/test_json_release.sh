#!/bin/bash

# Test script to create a GitHub Release with JSON files only to prove the CDN concept

set -e

# Configuration
REPO="AI-Mobility-Research-Lab/UMDL2"
VERSION="v1.0.1-test"
TITLE="UMDL2 JSON Test Release ${VERSION}"
NOTES="Test release with JSON files to verify CDN functionality

## Purpose
Prove that GitHub Releases + jsDelivr CDN works for static files

## Test Files
- locations.json (location metadata)
- live traffic JSON files (3 locations)
- Total size: ~24 KB

## CDN Test URLs
\`\`\`
https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/locations.json
https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/74th-Amsterdam-Columbus.json
\`\`\`
"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Creating JSON-only test release to prove CDN concept${NC}"
echo -e "Repository: ${YELLOW}${REPO}${NC}"
echo -e "Version: ${YELLOW}${VERSION}${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# JSON files to test
JSON_FILES=(
    "public/data/locations.json"
    "public/data/live-traffic/74th-Amsterdam-Columbus.json"
    "public/data/live-traffic/Amsterdam-80th.json"
    "public/data/live-traffic/Columbus-86th.json"
)

# Check if all files exist
echo -e "${YELLOW}📋 Checking JSON files...${NC}"
for json_file in "${JSON_FILES[@]}"; do
    if [ ! -f "$json_file" ]; then
        echo -e "${RED}❌ Missing file: $json_file${NC}"
        exit 1
    else
        size=$(du -h "$json_file" | cut -f1)
        echo -e "  ✅ $json_file (${size})"
    fi
done

# Calculate total size
TOTAL_SIZE=$(du -ch "${JSON_FILES[@]}" | grep total | cut -f1)
echo -e "${GREEN}📦 Total size: ${TOTAL_SIZE} (perfect for testing)${NC}"
echo ""

# Delete existing test release if it exists
if gh release view "$VERSION" --repo "$REPO" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Deleting existing test release...${NC}"
    gh release delete "$VERSION" --repo "$REPO" --yes
fi

# Create the release
echo -e "${GREEN}📤 Creating test release with JSON files...${NC}"

gh release create "$VERSION" \
    "${JSON_FILES[@]}" \
    --repo "$REPO" \
    --title "$TITLE" \
    --notes "$NOTES" \
    --prerelease

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Test release created successfully!${NC}"
    echo ""
    echo -e "${GREEN}🌐 Test CDN URLs:${NC}"
    echo ""
    echo "jsDelivr CDN (should work in 1-5 minutes):"
    for json_file in "${JSON_FILES[@]}"; do
        filename=$(basename "$json_file")
        echo "  https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/${filename}"
    done
    echo ""
    echo "Direct GitHub URLs (should work immediately):"
    for json_file in "${JSON_FILES[@]}"; do
        filename=$(basename "$json_file")
        echo "  https://github.com/${REPO}/releases/download/${VERSION}/${filename}"
    done
    echo ""
    echo -e "${YELLOW}🧪 Test Commands:${NC}"
    echo ""
    echo "# Test direct GitHub access (immediate):"
    echo "curl -s https://github.com/${REPO}/releases/download/${VERSION}/locations.json | jq ."
    echo ""
    echo "# Test jsDelivr CDN (1-5 min delay):"
    echo "curl -s https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/locations.json | jq ."
    echo ""
    echo "# Check HTTP status:"
    echo "curl -I https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/locations.json"
    
else
    echo -e "${RED}❌ Failed to create test release${NC}"
    exit 1
fi