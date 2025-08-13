#!/bin/bash
# Test script to verify processed videos are accessible

echo "🧪 Testing Processed Video Access"
echo "================================="
echo ""

API_URL="http://classificationbackend.boshang.online"

echo "1. Testing API Health:"
curl -s "$API_URL/health" | jq '.' || echo "Health check failed"
echo ""

echo "2. Testing Processing Status for Each Location:"
for location in "74th-Amsterdam-Columbus" "Amsterdam-80th" "Columbus-86th"; do
    echo "   Location: $location"
    response=$(curl -s "$API_URL/processing-status/$location")
    echo "   Response: $response"
    
    # Extract file path if available
    file_path=$(echo "$response" | jq -r '.files[0]' 2>/dev/null)
    if [ "$file_path" != "null" ] && [ -n "$file_path" ]; then
        echo "   ✅ Processed video found: $file_path"
        
        # Test if video is accessible
        video_url="$API_URL$file_path"
        http_status=$(curl -s -o /dev/null -w "%{http_code}" -I "$video_url")
        if [ "$http_status" = "200" ]; then
            echo "   ✅ Video file accessible (HTTP $http_status)"
        else
            echo "   ❌ Video file not accessible (HTTP $http_status)"
        fi
    else
        echo "   ❌ No processed video found"
    fi
    echo ""
done

echo "3. Summary:"
echo "   API Backend: $API_URL"
echo "   Frontend: https://asdfghjklzxcvbnm.aimobilitylab.xyz/"
echo ""
echo "✨ Test complete!"