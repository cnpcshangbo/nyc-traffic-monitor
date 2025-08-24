// CDN Service for GitHub Releases + jsDelivr hosting
import { getVideoUrl, DATA_URLS, isCDNConfigured } from '../config/cdn';
import { getApiBaseUrl } from '../config/api';

export interface Location {
  id: string;
  name: string;
  coordinates?: [number, number];
  original_video: string;
  has_processed: boolean;
  processed_files: string[];
}

export interface LiveTrafficData {
  location_id: string;
  timestamp: string;
  total_vehicles: number;
  vehicle_types: Record<string, number>;
  time_periods: Array<{
    period: string;
    start_time: string;
    end_time: string;
    vehicle_count: number;
    vehicle_types: Record<string, number>;
  }>;
}

class CDNService {
  private apiBaseUrl = getApiBaseUrl();

  async fetchLocations(): Promise<Location[]> {
    try {
      // Check if running on GitHub Pages (HTTPS) - skip HTTP backend due to Mixed Content Policy
      const isGitHubPages = window.location.hostname.includes('github.io');
      
      if (isCDNConfigured()) {
        // Try CDN first
        const response = await fetch(DATA_URLS.locations);
        if (response.ok) {
          const data = await response.json();
          return data.locations || [];
        }
      }
      
      if (isGitHubPages) {
        // GitHub Pages blocks HTTP requests - use fallback data immediately
        console.log('GitHub Pages detected - using fallback data (Mixed Content Policy blocks HTTP API)');
        return this.getFallbackLocations();
      }
      
      // Try backend API for non-GitHub Pages sites
      const response = await fetch(`${this.apiBaseUrl}/locations`);
      if (response.ok) {
        const data = await response.json();
        return data.locations.map((loc: any) => ({
          id: loc.id,
          name: loc.name,
          coordinates: [40.7831, -73.9778], // Default coordinates
          original_video: loc.original_video || '',
          has_processed: loc.has_processed || false,
          processed_files: loc.processed_files || []
        }));
      }
      
      throw new Error(`Failed to fetch locations: ${response.status}`);
    } catch (error) {
      console.error('Error fetching locations:', error);
      // Return fallback locations
      return this.getFallbackLocations();
    }
  }

  async fetchLiveTrafficData(locationId: string): Promise<LiveTrafficData | null> {
    try {
      const response = await fetch(DATA_URLS.liveTraffic(locationId));
      if (response.ok) {
        return await response.json();
      }
      
      console.warn(`No live traffic data found for ${locationId}`);
      return null;
    } catch (error) {
      console.error('Error fetching live traffic data:', error);
      return null;
    }
  }

  getVideoUrl(location: Location, useProcessed: boolean = true): string {
    const isGitHubPages = window.location.hostname.includes('github.io');
    
    if (isCDNConfigured()) {
      // Use CDN URLs
      return getVideoUrl(location.id, useProcessed);
    }
    
    if (isGitHubPages) {
      // GitHub Pages demo - use a placeholder message
      console.log('GitHub Pages: Video URLs unavailable due to Mixed Content Policy (HTTPS → HTTP blocked)');
      return ''; // Will show "No video available" message
    }
    
    // Fallback to backend URLs for other sites
    if (useProcessed && location.has_processed && location.processed_files?.length > 0) {
      const processedFile = location.processed_files[0];
      return `${this.apiBaseUrl}/processed-videos/${processedFile}`;
    }
    
    // Use original video from backend
    if (location.original_video) {
      return `${this.apiBaseUrl}/videos/${location.id}_${location.original_video}`;
    }
    
    return '';
  }

  // Check if a video URL is accessible
  async checkVideoAvailability(url: string): Promise<boolean> {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      return response.ok;
    } catch (error) {
      console.error('Error checking video availability:', error);
      return false;
    }
  }

  // Get the best available video for a location
  async getBestVideoUrl(location: Location): Promise<string> {
    // Try processed video first
    if (location.has_processed && location.processed_files?.length > 0) {
      const processedUrl = this.getVideoUrl(location, true);
      const isAvailable = await this.checkVideoAvailability(processedUrl);
      if (isAvailable) {
        return processedUrl;
      }
    }

    // Fallback to original video
    const originalUrl = this.getVideoUrl(location, false);
    return originalUrl;
  }

  private getFallbackLocations(): Location[] {
    return [
      {
        id: "74th-Amsterdam-Columbus",
        name: "Richmond Hill Road & Edinboro Rd, Staten Island",
        coordinates: [40.5372, -74.2435],
        original_video: "2025-02-13_06-00-04.mp4",
        has_processed: true,
        processed_files: ["74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4"]
      },
      {
        id: "Amsterdam-80th",
        name: "Arthur Kill Rd & Storer Ave, Staten Island", 
        coordinates: [40.5784, -74.2367],
        original_video: "2025-02-13_06-00-04.mp4",
        has_processed: true,
        processed_files: ["Amsterdam-80th_adjusted_loop_full_demo.mp4"]
      },
      {
        id: "Columbus-86th",
        name: "Katonah Ave & East 241st St, Bronx",
        coordinates: [40.8931, -73.8675], 
        original_video: "2025-02-13_06-00-06.mp4",
        has_processed: true,
        processed_files: ["Columbus-86th_adjusted_loop_full_demo.mp4"]
      }
    ];
  }
}

export const cdnService = new CDNService();