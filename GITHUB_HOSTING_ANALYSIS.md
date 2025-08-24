# GitHub vs S3 Hosting Analysis for UMDL2

## Current File Sizes

### Required Videos (6 files = 1.38 GB total):

**Processed Videos (763 MB):**
- `74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4`: 270 MB
- `Amsterdam-80th_adjusted_loop_full_demo.mp4`: 94 MB
- `Columbus-86th_adjusted_loop_full_demo.mp4`: 399 MB

**Original Videos (616 MB):**
- `74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4`: 241 MB
- `Amsterdam-80th_2025-02-13_06-00-04.mp4`: 82 MB
- `Columbus-86th_2025-02-13_06-00-06.mp4`: 293 MB

## ❌ GitHub Pages Direct Hosting - NOT FEASIBLE

### Limitations:
1. **File size limit**: 100 MB per file (5 of 6 videos exceed this)
2. **Repository size**: 1 GB recommended, 5 GB hard limit
3. **GitHub Pages size**: 1 GB total limit
4. **Total size needed**: 1.38 GB (exceeds limit)

### Problems:
- Would need Git LFS for large files
- Git LFS free tier: only 1 GB bandwidth/month
- Makes repository heavy and slow to clone
- Poor video streaming performance

## ✅ GitHub Releases Solution - RECOMMENDED

### How it works:
1. Upload videos as GitHub Release assets (up to 2 GB per file)
2. Use direct download URLs or CDN
3. Keep repository lightweight
4. Free, reliable hosting

### Advantages:
- **No file size limits** (up to 2 GB per file)
- **Free bandwidth** (within reasonable use)
- **CDN available** via jsDelivr
- **Keeps repo small** (faster clones)
- **Version control** for videos
- **No additional services needed**

### Implementation:

#### Step 1: Create a GitHub Release
```bash
# Create a new release with video assets
gh release create v1.0.0 \
  processed_videos/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4 \
  processed_videos/Amsterdam-80th_adjusted_loop_full_demo.mp4 \
  processed_videos/Columbus-86th_adjusted_loop_full_demo.mp4 \
  videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4 \
  videos/Amsterdam-80th_2025-02-13_06-00-04.mp4 \
  videos/Columbus-86th_2025-02-13_06-00-06.mp4 \
  --title "UMDL2 Video Assets v1.0.0" \
  --notes "Video files for Urban Mobility Data Living Laboratory"
```

#### Step 2: Access URLs

**Direct GitHub URLs** (rate limited):
```
https://github.com/AI-Mobility-Research-Lab/UMDL2/releases/download/v1.0.0/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
```

**jsDelivr CDN URLs** (recommended, cached globally):
```
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
```

## 📊 Comparison Table

| Feature | GitHub Pages | GitHub Releases | S3 |
|---------|--------------|-----------------|-----|
| **File size limit** | 100 MB | 2 GB | Unlimited |
| **Total storage** | 1 GB | Unlimited* | Unlimited |
| **Bandwidth** | Limited | Free* | Pay per GB |
| **Setup complexity** | ❌ Complex (LFS) | ✅ Simple | Medium |
| **Cost** | Free (limited) | Free | ~$5/month |
| **CDN** | GitHub's CDN | jsDelivr (free) | CloudFront |
| **HTTPS** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Reliability** | Good | Excellent | Excellent |
| **Streaming** | Poor | Good | Excellent |

*Within GitHub's fair use policy

## 🎯 Recommendation: GitHub Releases + jsDelivr

### Why this is better than S3 for your use case:
1. **Completely free** (no AWS account needed)
2. **Simple to implement** (10 minutes vs hours)
3. **Reliable CDN** via jsDelivr
4. **Version control** for videos
5. **No maintenance** required
6. **Works with existing GitHub workflow**

### Why this is better than GitHub Pages:
1. **No size limitations** that matter
2. **Better performance** (CDN optimized)
3. **Cleaner repository** (videos not in git)
4. **Easier updates** (just create new release)

## Quick Implementation Guide

### 1. Create the Release (one-time)
```bash
cd /home/roboticslab/City College Dropbox/BO SHANG/NYCDOT_classification_project/nyc-traffic-monitor

# Create release with all videos
gh release create v1.0.0 \
  backend/processed_videos/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4 \
  backend/processed_videos/Amsterdam-80th_adjusted_loop_full_demo.mp4 \
  backend/processed_videos/Columbus-86th_adjusted_loop_full_demo.mp4 \
  backend/videos/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4 \
  backend/videos/Amsterdam-80th_2025-02-13_06-00-04.mp4 \
  backend/videos/Columbus-86th_2025-02-13_06-00-06.mp4 \
  --repo AI-Mobility-Research-Lab/UMDL2 \
  --title "UMDL2 Video Assets v1.0.0" \
  --notes "Video files for traffic monitoring demos"
```

### 2. Update Frontend Configuration
```typescript
// src/config/cdn.ts
export const CDN_BASE = 'https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0';

export const VIDEO_URLS = {
  processed: {
    '74th-Amsterdam-Columbus': `${CDN_BASE}/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4`,
    'Amsterdam-80th': `${CDN_BASE}/Amsterdam-80th_adjusted_loop_full_demo.mp4`,
    'Columbus-86th': `${CDN_BASE}/Columbus-86th_adjusted_loop_full_demo.mp4`,
  },
  original: {
    '74th-Amsterdam-Columbus': `${CDN_BASE}/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4`,
    'Amsterdam-80th': `${CDN_BASE}/Amsterdam-80th_2025-02-13_06-00-04.mp4`,
    'Columbus-86th': `${CDN_BASE}/Columbus-86th_2025-02-13_06-00-06.mp4`,
  }
};
```

### 3. Include JSON files in repository
Since JSON files are small (few KB), include them directly in the repository:
```
public/
  data/
    locations.json
    live-traffic/
      74th-Amsterdam-Columbus.json
      Amsterdam-80th.json
      Columbus-86th.json
```

## Conclusion

**GitHub Releases + jsDelivr CDN** is the best solution for your needs:
- ✅ Free forever
- ✅ Simple 10-minute setup
- ✅ Excellent performance
- ✅ No size limitations
- ✅ No maintenance
- ✅ Works perfectly with GitHub Pages frontend

This eliminates the backend server completely while providing better performance than direct GitHub Pages hosting and avoiding the complexity/cost of S3.