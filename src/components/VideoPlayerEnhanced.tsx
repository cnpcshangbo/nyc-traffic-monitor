import React, { useRef, useEffect, useState, useCallback } from 'react';
import { ObjectDetectionService, Detection } from '../services/objectDetection';
import { API_ENDPOINTS } from '../config/api';

interface VideoPlayerEnhancedProps {
  videoPath: string;
  locationId: string;
  onTimeUpdate: (time: number) => void;
  onDetections?: (detections: Detection[]) => void;
}

const VideoPlayerEnhanced: React.FC<VideoPlayerEnhancedProps> = ({ 
  videoPath, 
  locationId,
  onTimeUpdate, 
  onDetections 
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [detectionService] = useState(() => new ObjectDetectionService());
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionInterval, setDetectionInterval] = useState<number>(500);
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.5);
  const [showControls, setShowControls] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [useProcessedVideo, setUseProcessedVideo] = useState(true); // Default to true
  const [processedVideoUrl, setProcessedVideoUrl] = useState<string | null>(null);
  const [isCheckingProcessed, setIsCheckingProcessed] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const animationRef = useRef<number>();
  const lastDetectionTime = useRef<number>(0);
  
  useEffect(() => {
    checkForProcessedVideo();
  }, [locationId]);
  
  const checkForProcessedVideo = async () => {
    setIsCheckingProcessed(true);
    setUseProcessedVideo(true); // Default to true when checking
    try {
      const response = await fetch(API_ENDPOINTS.processingStatus(locationId));
      const data = await response.json();
      
      if (data.status === 'completed' && data.files.length > 0) {
        setProcessedVideoUrl(API_ENDPOINTS.processedVideo(data.files[0]));
        setUseProcessedVideo(true); // Use processed video if available
      } else {
        setProcessedVideoUrl(null);
        setUseProcessedVideo(false); // Fall back to live detection if no processed video
      }
    } catch (error) {
      console.error('Error checking for processed video:', error);
      setProcessedVideoUrl(null);
      setUseProcessedVideo(false); // Fall back to live detection on error
    } finally {
      setIsCheckingProcessed(false);
    }
  };
  
  const triggerVideoProcessing = async () => {
    setIsProcessing(true);
    try {
      const videoFilename = videoPath.split('/').pop() || '';
      const response = await fetch(API_ENDPOINTS.processVideo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          location_id: locationId,
          video_filename: videoFilename
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'already_processed') {
        setProcessedVideoUrl(API_ENDPOINTS.processedVideo(data.output_path));
        setUseProcessedVideo(true);
        setIsProcessing(false);
      } else if (data.status === 'processing') {
        // Check periodically for completion
        const checkInterval = setInterval(async () => {
          const statusResponse = await fetch(API_ENDPOINTS.processingStatus(locationId));
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'completed' && statusData.files.length > 0) {
            setProcessedVideoUrl(API_ENDPOINTS.processedVideo(statusData.files[0]));
            setUseProcessedVideo(true);
            setIsProcessing(false);
            clearInterval(checkInterval);
          }
        }, 3000);
        
        // Clear interval after 5 minutes to prevent infinite polling
        setTimeout(() => {
          clearInterval(checkInterval);
          setIsProcessing(false);
        }, 300000);
      } else {
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Error triggering video processing:', error);
      setIsProcessing(false);
    }
  };
  
  useEffect(() => {
    if (!useProcessedVideo) {
      detectionService.initialize().then(() => {
        setIsModelLoaded(true);
        console.log('Object detection model loaded');
      }).catch(error => {
        console.error('Failed to load detection model:', error);
        setModelError('Failed to load AI model. Please refresh the page to try again.');
      });
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [detectionService, useProcessedVideo]);
  
  useEffect(() => {
    setVideoError(null);
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
    }
    if (!useProcessedVideo) {
      detectionService.clearHistory();
    }
  }, [videoPath, detectionService, useProcessedVideo]);
  
  const drawBoundingBoxes = useCallback((detections: Detection[]) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    detections.forEach(detection => {
      const [x, y, width, height] = detection.bbox;
      
      ctx.strokeStyle = getColorForClass(detection.class);
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);
      
      ctx.fillStyle = getColorForClass(detection.class);
      ctx.fillRect(x, y - 20, width, 20);
      
      ctx.fillStyle = 'white';
      ctx.font = '14px Arial';
      ctx.fillText(
        `${detection.class} (${Math.round(detection.score * 100)}%)`,
        x + 5,
        y - 5
      );
    });
  }, []);
  
  const getColorForClass = (className: string): string => {
    const colors: { [key: string]: string } = {
      'car': '#22c55e',
      'cars': '#22c55e',
      'truck': '#ef4444',
      'trucks': '#ef4444',
      'bus': '#3b82f6',
      'buses': '#3b82f6',
      'motorcycle': '#eab308',
      'motorcycles': '#eab308',
      'bicycle': '#a855f7',
      'bicycles': '#a855f7',
      'person': '#f97316',
      'pedestrian': '#f97316',
      'pedestrians': '#f97316'
    };
    return colors[className.toLowerCase()] || '#666666';
  };
  
  const performDetection = useCallback(async () => {
    if (!isModelLoaded || !videoRef.current || !isDetecting || useProcessedVideo) return;
    
    const now = Date.now();
    if (now - lastDetectionTime.current < detectionInterval) {
      animationRef.current = requestAnimationFrame(performDetection);
      return;
    }
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (canvas && video.videoWidth > 0 && !video.paused) {
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }
      
      try {
        const currentTime = video.currentTime;
        const allDetections = await detectionService.detectObjects(video, currentTime);
        
        const filteredDetections = allDetections.filter(d => d.score >= confidenceThreshold);
        
        drawBoundingBoxes(filteredDetections);
        
        if (onDetections) {
          onDetections(filteredDetections);
        }
        
        lastDetectionTime.current = now;
      } catch (error) {
        console.error('Detection error:', error);
      }
    }
    
    animationRef.current = requestAnimationFrame(performDetection);
  }, [isModelLoaded, isDetecting, detectionService, drawBoundingBoxes, onDetections, detectionInterval, confidenceThreshold, useProcessedVideo]);
  
  useEffect(() => {
    if (isDetecting && !useProcessedVideo) {
      performDetection();
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
  }, [isDetecting, performDetection, useProcessedVideo]);

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };
  
  const handlePlay = () => {
    if (!useProcessedVideo) {
      setIsDetecting(true);
    }
  };
  
  const handlePause = () => {
    setIsDetecting(false);
  };
  
  const handleEnded = () => {
    setIsDetecting(false);
  };
  
  const handleError = (event: any) => {
    console.error('Video error:', event);
    console.error('Current video URL:', currentVideoUrl);
    console.error('Use processed video:', useProcessedVideo);
    console.error('Processed video URL:', processedVideoUrl);
    
    // If processed video fails, try to fallback to original video
    if (useProcessedVideo && processedVideoUrl) {
      console.log('Processed video failed, falling back to original video');
      setUseProcessedVideo(false);
      setVideoError(null);
      return;
    }
    
    setVideoError(`Failed to load video: ${currentVideoUrl}. Please check the video file exists.`);
    setIsDetecting(false);
  };
  
  const handleLoadedMetadata = () => {
    console.log('Video metadata loaded');
    setVideoError(null);
  };

  const adjustedPath = videoPath.replace('../', '/');
  const currentVideoUrl = useProcessedVideo && processedVideoUrl ? processedVideoUrl : adjustedPath;
  
  console.log('Playing video:', currentVideoUrl, 'Processed:', useProcessedVideo);

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '800px' }}>
      <video
        ref={videoRef}
        src={currentVideoUrl}
        controls
        preload="metadata"
        style={{ width: '100%', height: 'auto', display: 'block' }}
        onTimeUpdate={handleTimeUpdate}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        onError={handleError}
        onLoadedMetadata={handleLoadedMetadata}
        onCanPlay={() => {
          console.log('Video can play:', currentVideoUrl);
          setVideoError(null);
        }}
      />
      
      {!useProcessedVideo && (
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none'
          }}
        />
      )}
      
      {!isCheckingProcessed && (
        <div style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '10px',
          borderRadius: '8px',
          fontSize: '14px',
          display: 'flex',
          gap: '10px',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={useProcessedVideo && !!processedVideoUrl}
              onChange={(e) => setUseProcessedVideo(e.target.checked)}
              disabled={!processedVideoUrl}
            />
            {processedVideoUrl ? 'Use Server-Processed Video' : 'Server-Processed Video (Not Available)'}
          </label>
          
          {!processedVideoUrl && (
            <button
              onClick={triggerVideoProcessing}
              disabled={isProcessing}
              style={{
                background: isProcessing ? '#6b7280' : '#3b82f6',
                border: 'none',
                color: 'white',
                padding: '5px 10px',
                borderRadius: '4px',
                cursor: isProcessing ? 'not-allowed' : 'pointer',
                fontSize: '12px'
              }}
            >
              {isProcessing ? 'Processing...' : 'Process with YOLOv8'}
            </button>
          )}
          
          {useProcessedVideo && processedVideoUrl && (
            <span style={{ color: '#22c55e', fontSize: '12px' }}>
              ✓ YOLOv8 Processed
            </span>
          )}
          
          <button
            onClick={() => {
              console.log('=== VIDEO DEBUG INFO ===');
              console.log('Current video URL:', currentVideoUrl);
              console.log('Processed video URL:', processedVideoUrl);
              console.log('Use processed:', useProcessedVideo);
              console.log('Original video path:', adjustedPath);
              console.log('Location ID:', locationId);
            }}
            style={{
              background: '#64748b',
              border: 'none',
              color: 'white',
              padding: '3px 6px',
              borderRadius: '3px',
              cursor: 'pointer',
              fontSize: '10px'
            }}
          >
            🐛 Debug
          </button>
        </div>
      )}
      
      {!useProcessedVideo && !isModelLoaded && !modelError && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '20px',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          Loading object detection model...
          <div style={{ marginTop: '10px', fontSize: '12px', opacity: 0.8 }}>
            This may take a few moments
          </div>
        </div>
      )}
      
      {modelError && !useProcessedVideo && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(220, 38, 38, 0.9)',
          color: 'white',
          padding: '20px',
          borderRadius: '8px',
          textAlign: 'center',
          maxWidth: '300px'
        }}>
          <div style={{ fontSize: '16px', marginBottom: '10px' }}>⚠️ Error</div>
          <div>{modelError}</div>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '15px',
              padding: '8px 16px',
              background: 'white',
              color: '#dc2626',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            Refresh Page
          </button>
        </div>
      )}
      
      {videoError && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'rgba(220, 38, 38, 0.9)',
          color: 'white',
          padding: '20px',
          borderRadius: '8px',
          textAlign: 'center',
          maxWidth: '300px',
          zIndex: 10
        }}>
          <div style={{ fontSize: '16px', marginBottom: '10px' }}>🎥 Video Error</div>
          <div>{videoError}</div>
        </div>
      )}
      
      {!useProcessedVideo && isModelLoaded && !videoError && (
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '10px',
          borderRadius: '8px',
          fontSize: '12px',
          maxWidth: '200px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowControls(!showControls)}
              style={{
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '11px'
              }}
            >
              ⚙️ {showControls ? 'Hide' : 'Show'} Controls
            </button>
            <span style={{ color: isDetecting ? '#4ade80' : '#fbbf24' }}>
              ● {isDetecting ? 'Detecting' : 'Paused'}
            </span>
          </div>
          
          {showControls && (
            <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '2px' }}>
                  Detection Interval: {detectionInterval}ms
                </label>
                <input
                  type="range"
                  min="100"
                  max="2000"
                  step="100"
                  value={detectionInterval}
                  onChange={(e) => setDetectionInterval(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '2px' }}>
                  Confidence: {Math.round(confidenceThreshold * 100)}%
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.1"
                  value={confidenceThreshold}
                  onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoPlayerEnhanced;