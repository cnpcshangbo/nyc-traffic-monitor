import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '@tensorflow/tfjs';

export interface Detection {
  bbox: [number, number, number, number]; // [x, y, width, height]
  class: string;
  score: number;
  timestamp: number;
}

export interface TrafficCount {
  cars: number;
  trucks: number;
  buses: number;
  motorcycles: number;
  bicycles: number;
  pedestrians: number;
}

export class ObjectDetectionService {
  private model: cocoSsd.ObjectDetection | null = null;
  private detectionHistory: Detection[] = [];
  
  async initialize() {
    try {
      console.log('Loading COCO-SSD model...');
      this.model = await cocoSsd.load();
      console.log('Model loaded successfully');
    } catch (error) {
      console.error('Failed to load model:', error);
      throw error;
    }
  }
  
  async detectObjects(videoElement: HTMLVideoElement, timestamp: number): Promise<Detection[]> {
    if (!this.model) {
      throw new Error('Model not initialized');
    }
    
    const predictions = await this.model.detect(videoElement);
    
    const detections: Detection[] = predictions.map(pred => ({
      bbox: pred.bbox as [number, number, number, number],
      class: this.mapToTrafficClass(pred.class),
      score: pred.score,
      timestamp
    }));
    
    // Store detections for history
    this.detectionHistory.push(...detections);
    
    return detections;
  }
  
  private mapToTrafficClass(cocoClass: string): string {
    const mapping: { [key: string]: string } = {
      'car': 'cars',
      'truck': 'trucks',
      'bus': 'buses',
      'motorcycle': 'motorcycles',
      'bicycle': 'bicycles',
      'person': 'pedestrians'
    };
    
    return mapping[cocoClass] || cocoClass;
  }
  
  getTrafficCount(detections: Detection[]): TrafficCount {
    const count: TrafficCount = {
      cars: 0,
      trucks: 0,
      buses: 0,
      motorcycles: 0,
      bicycles: 0,
      pedestrians: 0
    };
    
    detections.forEach(detection => {
      const vehicleType = detection.class as keyof TrafficCount;
      if (vehicleType in count) {
        count[vehicleType]++;
      }
    });
    
    return count;
  }
  
  getAggregatedData(startTime: number, endTime: number, intervalSeconds: number): Array<TrafficCount & { time: number }> {
    const aggregated: Array<TrafficCount & { time: number }> = [];
    
    for (let time = startTime; time < endTime; time += intervalSeconds) {
      const intervalDetections = this.detectionHistory.filter(
        d => d.timestamp >= time && d.timestamp < time + intervalSeconds
      );
      
      const count = this.getTrafficCount(intervalDetections);
      aggregated.push({ ...count, time });
    }
    
    return aggregated;
  }
  
  clearHistory() {
    this.detectionHistory = [];
  }
  
  exportToCSV(aggregationSeconds: number): string {
    const endTime = Math.max(...this.detectionHistory.map(d => d.timestamp), 0);
    const aggregatedData = this.getAggregatedData(0, endTime, aggregationSeconds);
    
    const headers = 'Time,Cars,Trucks,Buses,Motorcycles,Bicycles,Pedestrians,Total\n';
    const rows = aggregatedData.map(data => {
      const total = data.cars + data.trucks + data.buses + data.motorcycles + data.bicycles + data.pedestrians;
      const timeStr = new Date(data.time * 1000).toISOString().substr(11, 8); // HH:MM:SS
      return `${timeStr},${data.cars},${data.trucks},${data.buses},${data.motorcycles},${data.bicycles},${data.pedestrians},${total}`;
    }).join('\n');
    
    return headers + rows;
  }
}