import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { getApiBaseUrl } from '../config/api';

interface LiveTrafficData {
  start_time: string;
  last_update: string;
  total_vehicles: number;
  vehicle_types: { [key: string]: number };
  time_intervals: Array<{
    start_time: number;
    end_time: number;
    duration_seconds: number;
    vehicle_count: number;
    start_time_string: string;
    cumulative_total: number;
  }>;
  recent_detections: Array<{
    vehicle_id: number;
    class: string;
    confidence: number;
    timestamp: number;
    frame_number: number;
    time_string: string;
  }>;
  traffic_rate: {
    vehicles_per_minute: number;
    current_interval: number;
    peak_interval: number;
  };
  status: string;
  summary?: {
    total_processing_time_minutes: number;
    average_vehicles_per_minute: number;
    total_intervals: number;
    peak_interval_count: number;
  };
}

interface LiveTrafficChartProps {
  locationId: string;
}

const LiveTrafficChart: React.FC<LiveTrafficChartProps> = ({ locationId }) => {
  const [trafficData, setTrafficData] = useState<LiveTrafficData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLiveData = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/live-traffic/${locationId}`);
      if (response.ok) {
        const data = await response.json();
        setTrafficData(data);
        setError(null);
      } else if (response.status === 404) {
        setError('No live traffic data available for this location');
      } else {
        setError('Failed to fetch live traffic data');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveData();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      // Refresh every 5 seconds when auto-refresh is enabled
      interval = setInterval(fetchLiveData, 5000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [locationId, autoRefresh]);

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>Loading live traffic data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
        <h4>📊 Live Traffic Distribution</h4>
        <p>{error}</p>
        <button onClick={fetchLiveData} style={{ marginTop: '10px', padding: '5px 15px' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!trafficData) {
    return null;
  }

  // Prepare data for time series chart
  const timeSeriesData = trafficData.time_intervals.map((interval, index) => ({
    interval: index + 1,
    time: interval.start_time_string,
    vehicles: interval.vehicle_count,
    cumulative: interval.cumulative_total,
    timestamp: interval.start_time
  }));

  // Prepare data for vehicle types chart
  const vehicleTypesData = Object.entries(trafficData.vehicle_types).map(([type, count]) => ({
    type,
    count
  }));

  const formatTooltipTime = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  return (
    <div style={{ marginTop: '20px' }}>
      {/* Header with controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h4>📊 Live Traffic Distribution</h4>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <label style={{ display: 'flex', alignItems: 'center', fontSize: '14px' }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            Auto-refresh
          </label>
          <button onClick={fetchLiveData} style={{ padding: '5px 10px', fontSize: '12px' }}>
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px', 
        marginBottom: '20px' 
      }}>
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>Total Vehicles</h5>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
            {trafficData.total_vehicles}
          </div>
        </div>
        
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>Rate (per minute)</h5>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
            {trafficData.traffic_rate.vehicles_per_minute}
          </div>
        </div>
        
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>Peak Interval</h5>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fd7e14' }}>
            {trafficData.traffic_rate.peak_interval}
          </div>
        </div>
        
        <div style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h5 style={{ margin: '0 0 10px 0', color: '#495057' }}>Status</h5>
          <div style={{ 
            fontSize: '16px', 
            fontWeight: 'bold', 
            color: trafficData.status === 'active' ? '#28a745' : '#6c757d' 
          }}>
            {trafficData.status === 'active' ? '🟢 Live' : '⏹️ Complete'}
          </div>
        </div>
      </div>

      {/* Time Series Chart */}
      {timeSeriesData.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h5 style={{ marginBottom: '15px' }}>Traffic Over Time (15-second intervals)</h5>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                labelFormatter={(label, payload) => {
                  if (payload && payload[0]) {
                    return `Time: ${label}`;
                  }
                  return label;
                }}
                formatter={(value, name) => [value, name === 'vehicles' ? 'Vehicles' : 'Cumulative']}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="vehicles" 
                stroke="#8884d8" 
                name="Vehicles per interval"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="cumulative" 
                stroke="#82ca9d" 
                name="Cumulative total"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Vehicle Types Chart */}
      {vehicleTypesData.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h5 style={{ marginBottom: '15px' }}>Vehicle Types Distribution</h5>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={vehicleTypesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Recent Detections */}
      {trafficData.recent_detections.length > 0 && (
        <div>
          <h5 style={{ marginBottom: '15px' }}>Recent Detections</h5>
          <div style={{ 
            maxHeight: '200px', 
            overflowY: 'auto', 
            backgroundColor: '#f8f9fa', 
            padding: '10px', 
            borderRadius: '8px',
            fontSize: '14px'
          }}>
            {trafficData.recent_detections.slice().reverse().map((detection, index) => (
              <div key={index} style={{ 
                padding: '8px', 
                marginBottom: '5px', 
                backgroundColor: 'white', 
                borderRadius: '4px',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>
                  <strong>ID:{detection.vehicle_id}</strong> {detection.class}
                </span>
                <span style={{ color: '#666' }}>
                  {detection.time_string} (conf: {(detection.confidence * 100).toFixed(1)}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Summary (if available) */}
      {trafficData.summary && (
        <div style={{ 
          marginTop: '20px', 
          padding: '15px', 
          backgroundColor: '#e9ecef', 
          borderRadius: '8px' 
        }}>
          <h5 style={{ marginBottom: '10px' }}>Processing Summary</h5>
          <div style={{ fontSize: '14px', color: '#495057' }}>
            <p>Processing time: {trafficData.summary.total_processing_time_minutes.toFixed(1)} minutes</p>
            <p>Average rate: {trafficData.summary.average_vehicles_per_minute.toFixed(2)} vehicles/minute</p>
            <p>Total intervals: {trafficData.summary.total_intervals}</p>
            <p>Peak interval: {trafficData.summary.peak_interval_count} vehicles</p>
          </div>
        </div>
      )}

      {/* Last update info */}
      <div style={{ 
        marginTop: '15px', 
        fontSize: '12px', 
        color: '#6c757d', 
        textAlign: 'center' 
      }}>
        Last updated: {new Date(trafficData.last_update).toLocaleString()}
      </div>
    </div>
  );
};

export default LiveTrafficChart;