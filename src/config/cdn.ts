// CDN Configuration for GitHub Releases + jsDelivr
// This provides free, fast, global CDN for video files hosted on GitHub Releases

// Update the version tag when you create a new release with updated videos
const RELEASE_VERSION = 'v1.0.0';
const GITHUB_REPO = 'AI-Mobility-Research-Lab/UMDL2';

// jsDelivr CDN - Recommended for production (cached, fast, global)
// export const CDN_BASE = `https://cdn.jsdelivr.net/gh/${GITHUB_REPO}@${RELEASE_VERSION}`;

// Alternative: Direct GitHub URLs (slower, rate limited, use for testing)
// Temporarily using direct GitHub while jsDelivr syncs (10-30 min delay)
export const CDN_BASE = `https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_VERSION}`;

// Video URLs configuration
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

// Static data files (these are small and can be in the repository)
export const DATA_URLS = {
  locations: '/data/locations.json',
  liveTraffic: (locationId: string) => `/data/live-traffic/${locationId}.json`,
};

// Helper function to get video URL
export const getVideoUrl = (locationId: string, useProcessed: boolean = true): string => {
  if (useProcessed && VIDEO_URLS.processed[locationId as keyof typeof VIDEO_URLS.processed]) {
    return VIDEO_URLS.processed[locationId as keyof typeof VIDEO_URLS.processed];
  }
  return VIDEO_URLS.original[locationId as keyof typeof VIDEO_URLS.original] || '';
};

// Check if CDN is properly configured (release exists)
export const isCDNConfigured = (): boolean => {
  // CDN is being configured - GitHub Release v1.0.0 exists but may need time to propagate
  // Temporarily using backend fallback until CDN URLs are accessible (10-30 min)
  return false; // Change to true once CDN URLs are confirmed working
};