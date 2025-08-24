# Manual GitHub Release Creation Instructions

Since the GitHub CLI needs re-authentication, here's how to create the release manually:

## Option 1: Re-authenticate GitHub CLI (Recommended)

```bash
# Re-authenticate GitHub CLI
gh auth login -h github.com

# Follow the prompts to authenticate
# Then run the release script
./scripts/create_github_release.sh
```

## Option 2: Manual Release via GitHub Web Interface

### 1. Navigate to GitHub Repository
Go to: https://github.com/AI-Mobility-Research-Lab/UMDL2

### 2. Create a New Release
- Click "Releases" tab
- Click "Create a new release"
- Tag: `v1.0.0`
- Title: `UMDL2 Video Assets v1.0.0`

### 3. Upload Video Files
Upload these 6 files by dragging them to the release assets area:

**Processed Videos (from backend/processed_videos/):**
- `74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4` (270 MB)
- `Amsterdam-80th_adjusted_loop_full_demo.mp4` (94 MB) 
- `Columbus-86th_adjusted_loop_full_demo.mp4` (399 MB)

**Original Videos (from backend/videos/):**
- `74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4` (241 MB)
- `Amsterdam-80th_2025-02-13_06-00-04.mp4` (82 MB)
- `Columbus-86th_2025-02-13_06-00-06.mp4` (293 MB)

### 4. Release Description
```markdown
Video files for Urban Mobility Data Living Laboratory traffic monitoring demos

## Included Files
- 3 Processed videos with virtual loop overlays and tracking IDs
- 3 Original videos for comparison
- Total size: ~1.4 GB

## CDN Access
Videos are automatically available via jsDelivr CDN:
```
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/[filename]
```

## Usage in Frontend
These videos replace the backend server for static file serving.
```

### 5. Publish Release
- Check "Set as the latest release"
- Click "Publish release"

## Option 3: Quick CLI Authentication

```bash
# Quick GitHub token authentication
echo "YOUR_GITHUB_TOKEN" | gh auth login --with-token

# Replace YOUR_GITHUB_TOKEN with a personal access token
# Create token at: https://github.com/settings/tokens
# Permissions needed: repo, write:packages
```

## After Release is Created

The CDN URLs will be:
```
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/Amsterdam-80th_adjusted_loop_full_demo.mp4
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/Columbus-86th_adjusted_loop_full_demo.mp4
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/74th-Amsterdam-Columbus_2025-02-13_06-00-04.mp4
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/Amsterdam-80th_2025-02-13_06-00-04.mp4
https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/Columbus-86th_2025-02-13_06-00-06.mp4
```

## Test Video Access

After creating the release, test access with:
```bash
curl -I https://cdn.jsdelivr.net/gh/AI-Mobility-Research-Lab/UMDL2@v1.0.0/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4
```

Should return HTTP 200 OK.