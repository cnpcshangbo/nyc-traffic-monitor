// S3 Configuration for Static Assets
// Replace with your actual S3 bucket URL or CloudFront distribution

// Option 1: Direct S3 URL
export const S3_BASE_URL = 'https://umdl2-static.s3.amazonaws.com';

// Option 2: CloudFront CDN (faster, recommended for production)
// export const S3_BASE_URL = 'https://d1234567890.cloudfront.net';

// Option 3: Custom domain (if configured)
// export const S3_BASE_URL = 'https://static.umdl2.org';

export const S3_PATHS = {
  // Processed videos with bounding boxes
  processedVideo: (filename: string) => 
    `${S3_BASE_URL}/videos/processed/${filename}`,
  
  // Original videos
  originalVideo: (locationId: string, filename: string) => 
    `${S3_BASE_URL}/videos/original/${locationId}/${filename}`,
  
  // Live traffic JSON data
  liveTraffic: (locationId: string) => 
    `${S3_BASE_URL}/data/live-traffic/${locationId}.json`,
  
  // Static locations metadata
  locations: `${S3_BASE_URL}/data/locations.json`,
  
  // Loop configuration
  loopConfigs: `${S3_BASE_URL}/data/loop-configs.json`,
  
  // Verification images
  verificationImage: (filename: string) => 
    `${S3_BASE_URL}/images/${filename}`,
};

// Check if S3 is configured (for fallback to backend)
export const isS3Configured = (): boolean => {
  return S3_BASE_URL.length > 0 && !S3_BASE_URL.includes('REPLACE_WITH_YOUR');
};

// Helper to get video URL with fallback
export const getVideoUrl = (
  filename: string, 
  fallbackUrl?: string
): string => {
  if (isS3Configured()) {
    return S3_PATHS.processedVideo(filename);
  }
  return fallbackUrl || '';
};