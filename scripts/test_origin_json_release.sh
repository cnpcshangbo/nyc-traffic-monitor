#!/bin/bash

# Test JSON release on the origin repository (cnpcshangbo/nyc-traffic-monitor)

set -e

REPO="cnpcshangbo/nyc-traffic-monitor"
VERSION="v1.0.1-json-test"
TITLE="JSON CDN Test Release"

echo "🧪 Testing GitHub Release CDN concept with origin repository"
echo "Repository: $REPO"
echo "Version: $VERSION"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# JSON files to test
JSON_FILES=(
    "public/data/locations.json"
    "public/data/live-traffic/74th-Amsterdam-Columbus.json"
)

# Delete existing test release if it exists
if gh release view "$VERSION" --repo "$REPO" &> /dev/null; then
    echo "⚠️  Deleting existing test release..."
    gh release delete "$VERSION" --repo "$REPO" --yes
fi

echo "📤 Creating test release..."

gh release create "$VERSION" \
    "${JSON_FILES[@]}" \
    --repo "$REPO" \
    --title "$TITLE" \
    --notes "Test release to verify GitHub CDN functionality with JSON files" \
    --prerelease

echo ""
echo "✅ Release created!"
echo ""
echo "🧪 Test URLs:"
echo ""
echo "Direct GitHub (immediate):"
echo "  https://github.com/${REPO}/releases/download/${VERSION}/locations.json"
echo ""
echo "jsDelivr CDN (1-5 min delay):"
echo "  https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/locations.json"
echo ""
echo "Test commands:"
echo "  curl -s https://github.com/${REPO}/releases/download/${VERSION}/locations.json"
echo "  curl -I https://cdn.jsdelivr.net/gh/${REPO}@${VERSION}/locations.json"