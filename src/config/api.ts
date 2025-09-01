// API configuration for different environments
export const getApiBaseUrl = (): string => {
  // 1) Explicit override via Vite env
  const envUrl = import.meta.env?.VITE_API_URL as string | undefined;
  const isSecurePage = typeof window !== 'undefined' && window.location.protocol === 'https:';
  if (envUrl && typeof envUrl === 'string' && envUrl.trim().length > 0) {
    const cleaned = envUrl.replace(/\/$/, '');
    // Avoid mixed-content: ignore http:// API when page is served over https
    if (isSecurePage && cleaned.startsWith('http://')) {
      // fall through to hostname-based defaults below
    } else {
      return cleaned;
    }
  }

  // 2) Hostname-based defaults for deployed environments
  const host = typeof window !== 'undefined' ? window.location.hostname : '';
  // Same-origin when frontend is served from the backend domain
  if (host === 'classificationbackend.boshang.online') {
    return window.location.origin;
  }
  if (host === 'classification.boshang.online' ||
      host === 'asdfghjklzxcvbnm.aimobilitylab.xyz' ||
      host === 'cnpcshangbo.github.io' ||
      host === 'ai-mobility-research-lab.github.io') {
    return 'https://classificationbackend.boshang.online';
  }

  // 3) Fallback to localhost for local development
  return 'http://localhost:8001';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  processingStatus: (locationId: string) => `${API_BASE_URL}/processing-status/${encodeURIComponent(locationId)}`,
  processVideo: `${API_BASE_URL}/process-video`,
  processedVideo: (path: string) => `${API_BASE_URL}${path}`,
  health: `${API_BASE_URL}/health`,
  locations: `${API_BASE_URL}/locations`,
};

// Helper: identify production-like hosts where we want deterministic demo UX
export const isProdDemoHost = (): boolean => {
  if (typeof window === 'undefined') return false;
  const host = window.location.hostname;
  return (
    host === 'classification.boshang.online' ||
    host === 'asdfghjklzxcvbnm.aimobilitylab.xyz' ||
    host === 'cnpcshangbo.github.io' ||
    host === 'ai-mobility-research-lab.github.io'
  );
};
