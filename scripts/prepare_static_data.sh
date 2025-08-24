#!/bin/bash

# Script to prepare static JSON data files for GitHub Pages deployment
# These small files can be included directly in the repository

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📊 Preparing static data files for GitHub Pages${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Create data directory structure in public
mkdir -p public/data/live-traffic

# Copy locations.json (already generated)
if [ -f "backend/static_metadata/locations.json" ]; then
    cp backend/static_metadata/locations.json public/data/
    echo -e "✅ Copied locations.json"
else
    echo -e "${YELLOW}⚠️  Creating locations.json...${NC}"
    cat > public/data/locations.json << 'EOF'
{
  "locations": [
    {
      "id": "74th-Amsterdam-Columbus",
      "name": "Richmond Hill Road & Edinboro Rd, Staten Island",
      "coordinates": [40.5372, -74.2435],
      "original_video": "2025-02-13_06-00-04.mp4",
      "has_processed": true,
      "processed_files": ["74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4"]
    },
    {
      "id": "Amsterdam-80th",
      "name": "Arthur Kill Rd & Storer Ave, Staten Island",
      "coordinates": [40.5784, -74.2367],
      "original_video": "2025-02-13_06-00-04.mp4",
      "has_processed": true,
      "processed_files": ["Amsterdam-80th_adjusted_loop_full_demo.mp4"]
    },
    {
      "id": "Columbus-86th",
      "name": "Katonah Ave & East 241st St, Bronx",
      "coordinates": [40.8931, -73.8675],
      "original_video": "2025-02-13_06-00-06.mp4",
      "has_processed": true,
      "processed_files": ["Columbus-86th_adjusted_loop_full_demo.mp4"]
    }
  ]
}
EOF
    echo -e "✅ Created locations.json"
fi

# Copy live traffic JSON files
for location in "74th-Amsterdam-Columbus" "Amsterdam-80th" "Columbus-86th"; do
    src_file="backend/processed_videos/live_traffic_${location}.json"
    dest_file="public/data/live-traffic/${location}.json"
    
    if [ -f "$src_file" ]; then
        cp "$src_file" "$dest_file"
        echo -e "✅ Copied live traffic data for ${location}"
    else
        # Create a sample file if it doesn't exist
        echo -e "${YELLOW}⚠️  Creating sample data for ${location}...${NC}"
        cat > "$dest_file" << EOF
{
  "location_id": "${location}",
  "timestamp": "$(date -Iseconds)",
  "total_vehicles": 0,
  "vehicle_types": {
    "PC": 0,
    "Bus": 0,
    "Truck": 0,
    "Bk/Mc": 0
  },
  "time_periods": []
}
EOF
        echo -e "✅ Created sample data for ${location}"
    fi
done

# Create a simple index file for the data directory
cat > public/data/index.json << EOF
{
  "description": "UMDL2 Static Data Files",
  "files": {
    "locations": "/data/locations.json",
    "live_traffic": {
      "74th-Amsterdam-Columbus": "/data/live-traffic/74th-Amsterdam-Columbus.json",
      "Amsterdam-80th": "/data/live-traffic/Amsterdam-80th.json",
      "Columbus-86th": "/data/live-traffic/Columbus-86th.json"
    }
  },
  "updated": "$(date -Iseconds)"
}
EOF

echo -e "✅ Created data index file"

# Show summary
echo ""
echo -e "${GREEN}📁 Data structure created:${NC}"
tree public/data/ 2>/dev/null || ls -la public/data/

# Calculate total size
TOTAL_SIZE=$(du -sh public/data/ | cut -f1)
echo ""
echo -e "${GREEN}📦 Total data size: ${TOTAL_SIZE} (safe for git)${NC}"

echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Review the data files in public/data/"
echo "2. Commit and push to GitHub"
echo "3. Data will be available at: https://[your-github-pages-url]/data/"
echo ""
echo "Example URLs:"
echo "  https://ai-mobility-research-lab.github.io/UMDL2/data/locations.json"
echo "  https://ai-mobility-research-lab.github.io/UMDL2/data/live-traffic/74th-Amsterdam-Columbus.json"