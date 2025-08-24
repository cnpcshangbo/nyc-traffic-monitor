// S3 Service for fetching static assets
import { S3_PATHS, isS3Configured } from '../config/s3';
import { getApiBaseUrl } from '../config/api';

export interface Location {
  id: string;
  name: string;
  original_video: string;
  original_video_url?: string;
  has_processed: boolean;
  processed_files: string[];
}

export interface LiveTrafficData {
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

class S3Service {
  private useS3: boolean;
  private apiBaseUrl: string;

  constructor() {
    this.useS3 = isS3Configured();
    this.apiBaseUrl = getApiBaseUrl();
  }

  async fetchLocations(): Promise<Location[]> {
    try {
      if (this.useS3) {
        // Try S3 first
        const response = await fetch(S3_PATHS.locations);
        if (response.ok) {
          const data = await response.json();
          return data.locations || data;
        }
      }
      
      // Fallback to backend API
      const response = await fetch(`${this.apiBaseUrl}/locations`);
      if (response.ok) {
        const data = await response.json();
        return data.locations || [];
      }
      
      throw new Error('Failed to fetch locations');
    } catch (error) {
      console.error('Error fetching locations:', error);
      // Return default locations as last resort
      return this.getDefaultLocations();
    }
  }

  async fetchLiveTrafficData(locationId: string): Promise<LiveTrafficData | null> {
    try {
      if (this.useS3) {
        // Try S3 first
        const response = await fetch(S3_PATHS.liveTraffic(locationId));
        if (response.ok) {
          return await response.json();
        }
      }
      
      // Fallback to backend API
      const response = await fetch(`${this.apiBaseUrl}/live-traffic/${locationId}`);
      if (response.ok) {
        return await response.json();
      }
      
      return null;
    } catch (error) {
      console.error('Error fetching live traffic data:', error);
      return null;
    }
  }

  getVideoUrl(location: Location): string {
    // Check for processed videos first
    if (location.has_processed && location.processed_files?.length > 0) {
      const processedFile = location.processed_files[0];
      
      if (this.useS3) {
        return S3_PATHS.processedVideo(processedFile);
      } else {
        return `${this.apiBaseUrl}/processed-videos/${processedFile}`;
      }
    }
    
    // Fallback to original video
    if (location.original_video) {
      if (this.useS3) {
        return S3_PATHS.originalVideo(location.id, location.original_video);
      } else if (location.original_video_url) {
        return `${this.apiBaseUrl}${location.original_video_url}`;
      }
    }
    
    return '';
  }

  private getDefaultLocations(): Location[] {
    // Hardcoded fallback locations
    return [
      {
        id: "74th-Amsterdam-Columbus",
        name: "Richmond Hill Road & Edinboro Rd, Staten Island",
        original_video: "2025-02-13_06-00-04.mp4",
        has_processed: true,
        processed_files: ["74th-Amsterdam-Columbus_adjusted_loop_full_demo.mp4"]
      },
      {
        id: "Amsterdam-80th",
        name: "Arthur Kill Rd & Storer Ave, Staten Island",
        original_video: "2025-02-13_06-00-04.mp4",
        has_processed: true,
        processed_files: ["Amsterdam-80th_adjusted_loop_full_demo.mp4"]
      },
      {
        id: "Columbus-86th",
        name: "Katonah Ave & East 241st St, Bronx",
        original_video: "2025-02-13_06-00-06.mp4",
        has_processed: true,
        processed_files: ["Columbus-86th_adjusted_loop_full_demo.mp4"]
      }
    ];
  }
}

export const s3Service = new S3Service();