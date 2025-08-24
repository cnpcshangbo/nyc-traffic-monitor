// API configuration for different environments
export const getApiBaseUrl = (): string => {
  // Check if we're running on the external domains
  if (window.location.hostname === 'classification.boshang.online') {
    return 'http://classificationbackend.boshang.online';
  }
  
  if (window.location.hostname === 'asdfghjklzxcvbnm.aimobilitylab.xyz') {
    // Use the dedicated backend subdomain
    return 'http://classificationbackend.boshang.online';
  }
  
  // GitHub Pages domains
  if (window.location.hostname === 'cnpcshangbo.github.io' || 
      window.location.hostname === 'ai-mobility-research-lab.github.io') {
    return 'http://classificationbackend.boshang.online';
  }
  
  // Default to localhost for local development
  return 'http://localhost:8001';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  processingStatus: (locationId: string) => `${API_BASE_URL}/processing-status/${encodeURIComponent(locationId)}`,
  processVideo: `${API_BASE_URL}/process-video`,
  processedVideo: (path: string) => `${API_BASE_URL}${path}`,
  health: `${API_BASE_URL}/health`
};