import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, ResponsiveContainer } from 'recharts';

interface TrafficData {
  location_id: string;
  processing_timestamp: string;
  video_fps: number;
  total_crossings: number;
  interval_seconds: number;
  virtual_loops: {
    [loopName: string]: {
      total_count: number;
      vehicle_counts: { [vehicleType: string]: number };
      zone_points: number[][];
      direction: string;
    };
  };
  time_series: Array<{
    timestamp: number;
    interval_seconds: number;
    total_count: number;
    vehicle_counts: { [vehicleType: string]: number };
    crossings: Array<{
      vehicle_id: number;
      loop_name: string;
      class_name: string;
      confidence: number;
      direction: string;
      centroid: [number, number];
    }>;
  }>;
}

interface TrafficVolumeChartProps {
  locationId: string;
  currentTime?: number; // Current video playback time in seconds
  onTimeSelect?: (time: number) => void; // Callback when user clicks on chart
}

const TrafficVolumeChart: React.FC<TrafficVolumeChartProps> = ({ 
  locationId, 
  currentTime = 0, 
  onTimeSelect 
}) => {
  const [trafficData, setTrafficData] = useState<TrafficData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');

  const loadTrafficData = React.useCallback(async () => {
    if (!locationId) return;

    setLoading(true);
    setError(null);

    try {
      // Try to load traffic data JSON file for this location
      const jsonFileName = `${locationId}_traffic_data.json`;
      let response = await fetch(`${API_BASE_URL}/processed/${encodeURIComponent(jsonFileName)}`);
      // Fallback to legacy path if 404
      if (response.status === 404) {
        response = await fetch(`${API_BASE_URL}/processed-videos/${encodeURIComponent(jsonFileName)}`);
      }
      
      if (!response.ok) {
        if (response.status === 404) {
          setError('No traffic volume data available. Process video with virtual loops first.');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return;
      }

      const data: TrafficData = await response.json();
      setTrafficData(data);
      console.log('📊 Loaded traffic data:', {
        location: data.location_id,
        totalCrossings: data.total_crossings,
        loops: Object.keys(data.virtual_loops).length,
        timeIntervals: data.time_series.length
      });

    } catch (error) {
      console.error('Error loading traffic data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load traffic data');
    } finally {
      setLoading(false);
    }
  }, [locationId]);

  useEffect(() => {
    loadTrafficData();
  }, [loadTrafficData]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getChartData = () => {
    if (!trafficData) return [];

    return trafficData.time_series.map((interval) => ({
      time: formatTime(interval.timestamp),
      timestamp: interval.timestamp,
      totalCount: interval.total_count,
      PC: interval.vehicle_counts.PC || 0,
      Truck: interval.vehicle_counts.Truck || 0,
      Bus: interval.vehicle_counts.Bus || 0,
      'Bk/Mc': interval.vehicle_counts['Bk/Mc'] || 0,
      Ped: interval.vehicle_counts.Ped || 0,
    }));
  };

  const getVehicleColors = () => ({
    PC: '#22c55e',      // Green
    Truck: '#ef4444',   // Red
    Bus: '#3b82f6',     // Blue
    'Bk/Mc': '#eab308', // Yellow
    Ped: '#f97316',     // Orange
  });

  const getSummaryStats = () => {
    if (!trafficData) return null;

    const totalByType = Object.entries(trafficData.virtual_loops).reduce((acc, [, loop]) => {
      Object.entries(loop.vehicle_counts).forEach(([vehicleType, count]) => {
        acc[vehicleType] = (acc[vehicleType] || 0) + count;
      });
      return acc;
    }, {} as { [key: string]: number });

    return {
      totalCrossings: trafficData.total_crossings,
      totalByType,
      loopCount: Object.keys(trafficData.virtual_loops).length,
      duration: trafficData.time_series.length * trafficData.interval_seconds,
    };
  };

  if (loading) {
    return (
      <div className="traffic-chart-container">
        <div className="loading-indicator">
          <div className="loading-spinner"></div>
          <p>Loading traffic volume data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="traffic-chart-container">
        <div className="error-message">
          <h3>⚠️ Traffic Volume Data</h3>
          <p>{error}</p>
          <button onClick={loadTrafficData} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!trafficData) {
    return (
      <div className="traffic-chart-container">
        <div className="no-data-message">
          <h3>📊 Traffic Volume Analysis</h3>
          <p>No traffic data available for this location.</p>
        </div>
      </div>
    );
  }

  const chartData = getChartData();
  const summaryStats = getSummaryStats();
  const colors = getVehicleColors();

  return (
    <div className="traffic-chart-container">
      <div className="chart-header">
        <h3>🚦 Virtual Loop Traffic Volume</h3>
        <div className="chart-controls">
          <button 
            className={chartType === 'line' ? 'active' : ''}
            onClick={() => setChartType('line')}
          >
            Line Chart
          </button>
          <button 
            className={chartType === 'bar' ? 'active' : ''}
            onClick={() => setChartType('bar')}
          >
            Bar Chart
          </button>
        </div>
      </div>

      {summaryStats && (
        <div className="traffic-summary">
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-label">Total Crossings:</span>
              <span className="stat-value">{summaryStats.totalCrossings}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Virtual Loops:</span>
              <span className="stat-value">{summaryStats.loopCount}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Duration:</span>
              <span className="stat-value">{formatTime(summaryStats.duration)}</span>
            </div>
          </div>
          
          <div className="vehicle-breakdown">
            {Object.entries(summaryStats.totalByType).map(([vehicleType, count]) => (
              <div key={vehicleType} className="vehicle-stat">
                <div 
                  className="vehicle-color" 
                  style={{ backgroundColor: colors[vehicleType as keyof typeof colors] }}
                ></div>
                <span className="vehicle-type">{vehicleType}:</span>
                <span className="vehicle-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={300}>
          {chartType === 'line' ? (
            <LineChart data={chartData} onClick={(data) => onTimeSelect?.(data.activePayload?.[0]?.payload?.timestamp || 0)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
              />
              <YAxis />
              <Tooltip 
                labelStyle={{ color: '#333' }}
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
              <Legend />
              
              {Object.entries(colors).map(([vehicleType, color]) => (
                <Line 
                  key={vehicleType}
                  type="monotone" 
                  dataKey={vehicleType} 
                  stroke={color}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  connectNulls={false}
                />
              ))}
              
              {/* Current time indicator */}
              {currentTime > 0 && (
                <Line
                  type="monotone"
                  dataKey={() => null}
                  stroke="#ff0000"
                  strokeWidth={2}
                  strokeDasharray="5,5"
                  dot={false}
                />
              )}
            </LineChart>
          ) : (
            <BarChart data={chartData} onClick={(data) => onTimeSelect?.(data.activePayload?.[0]?.payload?.timestamp || 0)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
              />
              <YAxis />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '4px'
                }}
              />
              <Legend />
              
              {Object.entries(colors).map(([vehicleType, color]) => (
                <Bar 
                  key={vehicleType}
                  dataKey={vehicleType} 
                  fill={color}
                  stackId="vehicles"
                />
              ))}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      <div className="chart-info">
        <p>
          <strong>Virtual Loops:</strong> {Object.keys(trafficData.virtual_loops).join(', ')}
        </p>
        <p>
          <strong>Data Interval:</strong> {trafficData.interval_seconds}s | 
          <strong> Processing:</strong> {new Date(trafficData.processing_timestamp).toLocaleString()}
        </p>
      </div>

      <style jsx>{`
        .traffic-chart-container {
          background: white;
          border-radius: 8px;
          padding: 20px;
          margin: 20px 0;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .chart-header h3 {
          margin: 0;
          color: #1e293b;
          font-size: 1.2em;
        }

        .chart-controls {
          display: flex;
          gap: 8px;
        }

        .chart-controls button {
          padding: 6px 12px;
          border: 1px solid #d1d5db;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .chart-controls button:hover {
          background: #f3f4f6;
        }

        .chart-controls button.active {
          background: #3b82f6;
          color: white;
          border-color: #3b82f6;
        }

        .traffic-summary {
          display: flex;
          justify-content: space-between;
          margin-bottom: 20px;
          padding: 16px;
          background: #f8fafc;
          border-radius: 6px;
        }

        .summary-stats {
          display: flex;
          gap: 20px;
        }

        .stat-item {
          display: flex;
          flex-direction: column;
        }

        .stat-label {
          font-size: 12px;
          color: #64748b;
          margin-bottom: 2px;
        }

        .stat-value {
          font-size: 18px;
          font-weight: bold;
          color: #1e293b;
        }

        .vehicle-breakdown {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
        }

        .vehicle-stat {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .vehicle-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }

        .vehicle-type {
          font-size: 14px;
          color: #64748b;
        }

        .vehicle-count {
          font-size: 14px;
          font-weight: bold;
          color: #1e293b;
        }

        .chart-wrapper {
          margin: 20px 0;
        }

        .chart-info {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid #e5e7eb;
          font-size: 14px;
          color: #64748b;
        }

        .chart-info p {
          margin: 4px 0;
        }

        .loading-indicator, .error-message, .no-data-message {
          text-align: center;
          padding: 40px 20px;
        }

        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-message h3 {
          color: #dc2626;
          margin-bottom: 12px;
        }

        .retry-button {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 12px;
        }

        .retry-button:hover {
          background: #2563eb;
        }
      `}</style>
    </div>
  );
};

export default TrafficVolumeChart;
