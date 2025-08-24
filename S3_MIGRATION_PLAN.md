# S3 Migration Plan for UMDL2 Static Assets

## Current Architecture Analysis

### Backend is serving:
- **44 static files** (videos + JSON)
- **3.2 GB total data**:
  - `processed_videos/`: 2.6 GB (processed videos with bounding boxes)
  - `videos/`: 630 MB (original videos)
- **File types**:
  - `.mp4` videos (6 MB - 270 MB each)
  - `.json` files (traffic data, loop configurations)
  - `.jpg` verification images

### Current Backend Endpoints:
1. `/health` - Health check (keep)
2. `/processing-status/{location_id}` - Returns list of available files (simplify)
3. `/process-video` - Triggers video processing (remove/deprecate)
4. `/processed-videos/{filename}` - Serves video files (replace with S3)
5. `/videos/{filename}` - Serves original videos (replace with S3)
6. `/locations` - Returns location metadata (convert to static JSON)
7. `/live-traffic/{location_id}` - Serves JSON files (replace with S3)

## Migration Benefits

1. **Improved Stability**: S3 has 99.99% availability SLA
2. **Better Performance**: CloudFront CDN for global distribution
3. **Cost Reduction**: Eliminate backend server costs
4. **Simplified Architecture**: Frontend-only deployment
5. **Scalability**: No bandwidth limitations
6. **HTTPS Support**: S3 supports HTTPS natively

## S3 Bucket Structure

```
umdl2-static/
├── videos/
│   ├── original/
│   │   ├── 74th-Amsterdam-Columbus/
│   │   │   └── 2025-02-13_06-00-04.mp4
│   │   ├── Amsterdam-80th/
│   │   │   └── 2025-02-13_06-00-04.mp4
│   │   └── Columbus-86th/
│   │       └── 2025-02-13_06-00-06.mp4
│   └── processed/
│       ├── 74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
│       ├── Amsterdam-80th_adjusted_loop_full_demo.mp4
│       └── Columbus-86th_adjusted_loop_full_demo.mp4
├── data/
│   ├── locations.json (static location metadata)
│   ├── live-traffic/
│   │   ├── 74th-Amsterdam-Columbus.json
│   │   ├── Amsterdam-80th.json
│   │   └── Columbus-86th.json
│   └── loop-configs.json
└── images/
    ├── Amsterdam-80th_loop_verification.jpg
    └── Columbus-86th_loop_verification.jpg
```

## Implementation Steps

### Phase 1: S3 Setup
1. Create S3 bucket `umdl2-static` (or similar)
2. Configure public read access for static files
3. Enable CORS for cross-origin requests
4. Set up CloudFront distribution (optional but recommended)

### Phase 2: Upload Existing Files
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Sync files to S3
aws s3 sync backend/processed_videos/ s3://umdl2-static/videos/processed/ --acl public-read
aws s3 sync backend/videos/ s3://umdl2-static/videos/original/ --acl public-read
aws s3 cp backend/processed_videos/live_traffic_*.json s3://umdl2-static/data/live-traffic/ --acl public-read
```

### Phase 3: Frontend Updates

#### 1. Create S3 configuration
```typescript
// src/config/s3.ts
export const S3_BASE_URL = 'https://umdl2-static.s3.amazonaws.com';
// Or CloudFront: 'https://d1234567890.cloudfront.net'

export const S3_PATHS = {
  processedVideo: (filename: string) => `${S3_BASE_URL}/videos/processed/${filename}`,
  originalVideo: (location: string, filename: string) => `${S3_BASE_URL}/videos/original/${location}/${filename}`,
  liveTraffic: (locationId: string) => `${S3_BASE_URL}/data/live-traffic/${locationId}.json`,
  locations: `${S3_BASE_URL}/data/locations.json`,
};
```

#### 2. Update VideoPlayerEnhanced component
- Replace backend URLs with S3 URLs
- Remove dependency on `/processing-status` endpoint
- Use static `locations.json` for available videos

#### 3. Update App.tsx
- Fetch locations from S3 instead of backend API
- Update video URLs to point to S3

#### 4. Update LiveTrafficChart component
- Fetch JSON data directly from S3
- Remove backend API calls

### Phase 4: Static Metadata Generation

Create static JSON files to replace dynamic endpoints:

```javascript
// generate-static-metadata.js
const locations = [
  {
    id: "74th-Amsterdam-Columbus",
    name: "Richmond Hill Road & Edinboro Rd, Staten Island",
    original_video: "2025-02-13_06-00-04.mp4",
    processed_videos: [
      "74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4"
    ]
  },
  // ... other locations
];

fs.writeFileSync('locations.json', JSON.stringify(locations, null, 2));
```

### Phase 5: Deployment
1. Deploy updated frontend to GitHub Pages
2. Test all functionality with S3 URLs
3. Monitor for any issues
4. Deprecate backend server

## Cost Comparison

### Current (Backend Server):
- EC2/VPS: ~$10-50/month
- Bandwidth: Variable
- Maintenance: Ongoing

### S3 + CloudFront:
- Storage (3.2 GB): ~$0.08/month
- Requests: ~$0.01/1000 requests
- CloudFront: ~$0.085/GB transferred
- **Estimated total**: < $5/month for moderate traffic

## Fallback Plan

Keep backend running for 1 month after migration:
1. Frontend tries S3 first
2. Falls back to backend if S3 fails
3. Log any fallback usage
4. Fully deprecate after validation period

## Security Considerations

1. **S3 Bucket Policy**: Restrict to read-only public access
2. **CloudFront**: Use signed URLs for sensitive content (if needed)
3. **CORS Configuration**: Only allow specific origins
4. **Versioning**: Enable S3 versioning for rollback capability

## Timeline

- **Day 1**: Create S3 bucket, upload files
- **Day 2-3**: Update frontend code
- **Day 4**: Deploy and test
- **Day 5-7**: Monitor and fix issues
- **Week 2-4**: Parallel operation (both S3 and backend)
- **Month 2**: Deprecate backend

## Commands for Quick Migration

```bash
# Create bucket
aws s3 mb s3://umdl2-static

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket umdl2-static --policy file://bucket-policy.json

# Upload all files
aws s3 sync backend/processed_videos/ s3://umdl2-static/videos/processed/ --acl public-read
aws s3 sync backend/videos/ s3://umdl2-static/videos/original/ --acl public-read

# Test access
curl https://umdl2-static.s3.amazonaws.com/videos/processed/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
```

## Next Steps

1. Get AWS account credentials
2. Create S3 bucket
3. Start with Phase 1 implementation
4. Test with a single video file first
5. Gradually migrate all content