import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Detection, ObjectDetectionService, TrafficCount } from '../services/objectDetection';

interface TrafficChartProps {
  locationId: string;
  currentTime: number;
  detections?: Detection[];
  detectionService?: ObjectDetectionService;
}

interface TrafficData extends TrafficCount {
  time: number;
}

const TrafficChart: React.FC<TrafficChartProps> = ({ 
  locationId, 
  currentTime, 
  detections = [], 
  detectionService 
}) => {
  const [data, setData] = useState<TrafficData[]>([]);
  const [updateInterval, setUpdateInterval] = useState<NodeJS.Timeout | null>(null);
  const [isServerProcessed, setIsServerProcessed] = useState(false);

  // Check if we're likely using server-processed video (no recent detections)
  useEffect(() => {
    if (detections.length === 0 && currentTime > 5) {
      setIsServerProcessed(true);
    } else if (detections.length > 0) {
      setIsServerProcessed(false);
    }
  }, [detections, currentTime]);

  useEffect(() => {
    // Clear previous interval
    if (updateInterval) {
      clearInterval(updateInterval);
    }

    // Update chart data every second
    const interval = setInterval(() => {
      if (detectionService) {
        // Get aggregated data in 15-second intervals
        const aggregatedData = detectionService.getAggregatedData(0, currentTime + 1, 15);
        
        // Add empty data points for future time slots up to 5 minutes
        const maxTime = Math.max(300, currentTime + 60); // Show at least 5 minutes or current time + 1 minute
        for (let time = aggregatedData.length * 15; time <= maxTime; time += 15) {
          aggregatedData.push({
            time,
            cars: 0,
            trucks: 0,
            buses: 0,
            motorcycles: 0,
            bicycles: 0,
            pedestrians: 0
          });
        }
        
        setData(aggregatedData);
      }
    }, 1000);

    setUpdateInterval(interval);

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [currentTime, detectionService, locationId, updateInterval]);

  // Update current counts when new detections arrive
  useEffect(() => {
    if (detectionService && detections.length > 0) {
      const currentCount = detectionService.getTrafficCount(detections);
      console.log('Current traffic count:', currentCount);
    }
  }, [detections, detectionService]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate totals for display
  const currentTotal = detections.length;
  const overallStats = data.reduce((acc, item) => {
    acc.cars += item.cars;
    acc.trucks += item.trucks;
    acc.buses += item.buses;
    acc.motorcycles += item.motorcycles;
    acc.bicycles += item.bicycles;
    acc.pedestrians += item.pedestrians;
    return acc;
  }, {
    cars: 0,
    trucks: 0,
    buses: 0,
    motorcycles: 0,
    bicycles: 0,
    pedestrians: 0
  });

  return (
    <div style={{ width: '100%', height: '500px' }}>
      <h3>📡 Real-time Detection Volume</h3>
      
      {isServerProcessed ? (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          margin: '20px 0'
        }}>
          <h4 style={{ color: '#6c757d', marginBottom: '16px' }}>
            🎥 Server-Processed Video Mode
          </h4>
          <p style={{ color: '#6c757d', lineHeight: '1.5' }}>
            This video uses pre-processed detection data with embedded bounding boxes.<br/>
            Real-time detection data is not available in this mode.<br/>
            <strong>Check the "Virtual Loop Traffic Volume" chart below for traffic analysis.</strong>
          </p>
        </div>
      ) : (
        <>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            marginBottom: '20px',
            padding: '10px',
            backgroundColor: '#f5f5f5',
            borderRadius: '8px'
          }}>
            <div>
              <strong>Current Detections:</strong> {currentTotal}
            </div>
            <div>
              <strong>Total Counted:</strong> {Object.values(overallStats).reduce((a, b) => a + b, 0)}
            </div>
          </div>
      
      <ResponsiveContainer width="100%" height="80%">
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="time" 
            tickFormatter={formatTime}
            label={{ value: 'Time (mm:ss)', position: 'insideBottom', offset: -5 }}
          />
          <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            labelFormatter={(value) => `Time: ${formatTime(value as number)}`}
          />
          <Legend />
          
          <Line 
            type="monotone" 
            dataKey="cars" 
            stroke="#FF6B6B" 
            name="Cars" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="trucks" 
            stroke="#4ECDC4" 
            name="Trucks" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="buses" 
            stroke="#45B7D1" 
            name="Buses" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="motorcycles" 
            stroke="#FFA500" 
            name="Motorcycles" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="bicycles" 
            stroke="#98D8C8" 
            name="Bicycles" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="pedestrians" 
            stroke="#FFD93D" 
            name="Pedestrians" 
            strokeWidth={2}
            dot={false}
          />
          
          {currentTime > 0 && (
            <ReferenceLine 
              x={Math.floor(currentTime / 15) * 15} 
              stroke="red" 
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: "Current", position: "top" }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
        </>
      )}
    </div>
  );
};

export default TrafficChart;