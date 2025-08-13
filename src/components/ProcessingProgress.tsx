import React, { useState, useEffect } from 'react';

interface ProcessingJob {
  id: string;
  location: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  currentFrame: number;
  totalFrames: number;
  fps: number;
  timeElapsed: number;
  timeRemaining?: number;
  error?: string;
}

interface ProcessingProgressProps {
  onStartProcessing: (locationId: string) => void;
  availableLocations: Array<{ id: string; name: string }>;
}

const ProcessingProgress: React.FC<ProcessingProgressProps> = ({ 
  onStartProcessing, 
  availableLocations 
}) => {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [isPolling, setIsPolling] = useState(false);

  // Mock function to simulate backend API call for progress
  const fetchProcessingProgress = async (): Promise<ProcessingJob[]> => {
    try {
      // This would be a real API call to your backend
      // const response = await fetch('/api/processing/status');
      // return await response.json();
      
      // For now, return mock data based on current processing
      return jobs.map(job => {
        if (job.status === 'processing' && job.progress < 100) {
          return {
            ...job,
            progress: Math.min(job.progress + Math.random() * 2, 100),
            currentFrame: Math.floor((job.progress / 100) * job.totalFrames),
            fps: 24 + Math.random() * 4, // Simulate FPS variation
            timeElapsed: job.timeElapsed + 1
          };
        }
        return job;
      });
    } catch (error) {
      console.error('Failed to fetch processing progress:', error);
      return jobs;
    }
  };

  // Start processing for a location
  const handleStartProcessing = (locationId: string) => {
    const location = availableLocations.find(loc => loc.id === locationId);
    if (!location) return;

    const newJob: ProcessingJob = {
      id: `job-${Date.now()}`,
      location: location.name,
      status: 'processing',
      progress: 0,
      currentFrame: 0,
      totalFrames: 10977, // This would come from video analysis
      fps: 0,
      timeElapsed: 0
    };

    setJobs(prev => [...prev, newJob]);
    setIsPolling(true);
    onStartProcessing(locationId);
  };

  // Poll for progress updates
  useEffect(() => {
    if (!isPolling) return;

    const interval = setInterval(async () => {
      const updatedJobs = await fetchProcessingProgress();
      setJobs(updatedJobs);

      // Stop polling if all jobs are complete
      const hasActiveJobs = updatedJobs.some(job => 
        job.status === 'processing' || job.status === 'pending'
      );
      
      if (!hasActiveJobs) {
        setIsPolling(false);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isPolling, jobs]);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: ProcessingJob['status']): string => {
    switch (status) {
      case 'pending': return '#ffc107';
      case 'processing': return '#007bff';
      case 'completed': return '#28a745';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  return (
    <div className="processing-progress">
      <h3>🔬 YOLOv8 Server Processing</h3>
      
      <div className="processing-controls">
        <select 
          className="location-selector"
          onChange={(e) => e.target.value && handleStartProcessing(e.target.value)}
          defaultValue=""
        >
          <option value="" disabled>Select location to process</option>
          {availableLocations.map(location => (
            <option key={location.id} value={location.id}>
              {location.name}
            </option>
          ))}
        </select>
        <p className="processing-info">
          Server-side processing adds bounding boxes and classifications
        </p>
      </div>

      {jobs.length > 0 && (
        <div className="jobs-container">
          <h4>Processing Jobs</h4>
          {jobs.map(job => (
            <div key={job.id} className="job-card">
              <div className="job-header">
                <span className="job-location">{job.location}</span>
                <span 
                  className="job-status" 
                  style={{ color: getStatusColor(job.status) }}
                >
                  {job.status.toUpperCase()}
                </span>
              </div>
              
              <div className="progress-bar-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${job.progress}%`,
                      backgroundColor: getStatusColor(job.status)
                    }}
                  />
                </div>
                <span className="progress-text">{job.progress.toFixed(1)}%</span>
              </div>

              <div className="job-details">
                <div className="detail-row">
                  <span>Frames: {job.currentFrame.toLocaleString()} / {job.totalFrames.toLocaleString()}</span>
                  <span>FPS: {job.fps.toFixed(1)}</span>
                </div>
                <div className="detail-row">
                  <span>Elapsed: {formatTime(job.timeElapsed)}</span>
                  {job.timeRemaining && (
                    <span>Remaining: {formatTime(job.timeRemaining)}</span>
                  )}
                </div>
              </div>

              {job.error && (
                <div className="job-error">
                  ❌ Error: {job.error}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .processing-progress {
          margin: 20px 0;
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }

        .processing-progress h3 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .processing-controls {
          margin-bottom: 20px;
        }

        .location-selector {
          width: 100%;
          padding: 10px;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-size: 14px;
          background: white;
        }

        .processing-info {
          margin: 8px 0 0 0;
          font-size: 12px;
          color: #6c757d;
          font-style: italic;
        }

        .jobs-container h4 {
          margin: 0 0 15px 0;
          color: #495057;
        }

        .job-card {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          padding: 15px;
          margin-bottom: 10px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .job-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }

        .job-location {
          font-weight: bold;
          color: #495057;
        }

        .job-status {
          font-size: 12px;
          font-weight: bold;
          padding: 2px 6px;
          border-radius: 3px;
          background: rgba(0,0,0,0.1);
        }

        .progress-bar-container {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
        }

        .progress-bar {
          flex: 1;
          height: 20px;
          background: #e9ecef;
          border-radius: 10px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          transition: width 0.3s ease;
          border-radius: 10px;
        }

        .progress-text {
          font-size: 12px;
          font-weight: bold;
          color: #495057;
          min-width: 45px;
        }

        .job-details {
          font-size: 12px;
          color: #6c757d;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          margin-bottom: 4px;
        }

        .job-error {
          margin-top: 10px;
          padding: 8px;
          background: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
};

export default ProcessingProgress;