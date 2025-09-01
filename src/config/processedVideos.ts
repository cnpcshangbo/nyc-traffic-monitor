// Central mapping for known processed video overrides.
// Use absolute HTTPS URLs to avoid mixed-content issues.
// Keyed by `locationId` returned from the backend `locations` API.
export const PROCESSED_VIDEO_OVERRIDES: Record<string, string> = {
  // Example: maps a location ID to a published processed video
  // Ensure this stays in sync with backend identifiers.
  '74th-Amsterdam-Columbus':
    'https://classificationbackend.boshang.online/processed-videos/74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4',
};

export const getProcessedVideoOverride = (locationId: string): string | null => {
  const url = PROCESSED_VIDEO_OVERRIDES[locationId];
  return typeof url === 'string' && url.trim().length > 0 ? url : null;
};

// Default demo location id for auto-selection in production-like hosts
export const getDefaultDemoLocationId = (): string | null => {
  const keys = Object.keys(PROCESSED_VIDEO_OVERRIDES);
  return keys.length > 0 ? keys[0] : null;
};
