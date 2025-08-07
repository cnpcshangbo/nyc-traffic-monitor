import React, { useRef, useEffect, useState, useCallback } from 'react';
import ReactPlayer from 'react-player';
import { ObjectDetectionService, Detection } from '../services/objectDetection';

interface VideoPlayerProps {
  videoPath: string;
  onTimeUpdate: (time: number) => void;
  onDetections?: (detections: Detection[]) => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoPath, onTimeUpdate, onDetections }) => {
  const playerRef = useRef<ReactPlayer>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [detectionService] = useState(() => new ObjectDetectionService());
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [detectionInterval, setDetectionInterval] = useState<number>(500); // ms between detections
  const [confidenceThreshold, setConfidenceThreshold] = useState<number>(0.5);
  const [showControls, setShowControls] = useState(false);
  const [modelError, setModelError] = useState<string | null>(null);
  const [videoError, setVideoError] = useState<string | null>(null);
  const animationRef = useRef<number>();
  const lastDetectionTime = useRef<number>(0);
  
  useEffect(() => {
    // Initialize the detection model
    detectionService.initialize().then(() => {
      setIsModelLoaded(true);
      console.log('Object detection model loaded');
    }).catch(error => {
      console.error('Failed to load detection model:', error);
      setModelError('Failed to load AI model. Please refresh the page to try again.');
    });
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [detectionService]);
  
  useEffect(() => {
    // Reset player when video changes
    setVideoError(null); // Clear previous video errors
    if (playerRef.current && playerRef.current.seekTo) {
      try {
        playerRef.current.seekTo(0);
      } catch (error) {
        console.warn('Could not seek to start:', error);
      }
    }
    detectionService.clearHistory();
  }, [videoPath, detectionService]);
  
  const drawBoundingBoxes = useCallback((detections: Detection[]) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw each detection
    detections.forEach(detection => {
      const [x, y, width, height] = detection.bbox;
      
      // Draw bounding box
      ctx.strokeStyle = getColorForClass(detection.class);
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);
      
      // Draw label background
      ctx.fillStyle = getColorForClass(detection.class);
      ctx.fillRect(x, y - 20, width, 20);
      
      // Draw label text
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
      'cars': '#FF6B6B',
      'trucks': '#4ECDC4',
      'buses': '#45B7D1',
      'motorcycles': '#FFA500',
      'bicycles': '#98D8C8',
      'pedestrians': '#FFD93D'
    };
    return colors[className] || '#666666';
  };
  
  const performDetection = useCallback(async () => {
    if (!isModelLoaded || !videoRef.current || !isDetecting) return;
    
    const now = Date.now();
    if (now - lastDetectionTime.current < detectionInterval) {
      // Schedule next check
      animationRef.current = requestAnimationFrame(performDetection);
      return;
    }
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (canvas && video.videoWidth > 0) {
      // Update canvas size to match video (only once)
      if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
      }
      
      try {
        const currentTime = playerRef.current?.getCurrentTime?.() || 0;
        const allDetections = await detectionService.detectObjects(video, currentTime);
        
        // Filter detections by confidence threshold
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
    
    // Schedule next detection
    animationRef.current = requestAnimationFrame(performDetection);
  }, [isModelLoaded, isDetecting, detectionService, drawBoundingBoxes, onDetections, detectionInterval]);
  
  useEffect(() => {
    if (isDetecting) {
      performDetection();
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
  }, [isDetecting, performDetection]);

  const handleProgress = (state: { played: number; playedSeconds: number }) => {
    onTimeUpdate(state.playedSeconds);
    
    // Try to get video element if we don't have it yet
    if (!videoRef.current && playerRef.current) {
      try {
        const internalPlayer = playerRef.current.getInternalPlayer() as HTMLVideoElement;
        if (internalPlayer && internalPlayer.tagName === 'VIDEO') {
          videoRef.current = internalPlayer;
        }
      } catch (error) {
        // Ignore errors when trying to get internal player
      }
    }
  };
  
  const handlePlay = () => {
    setIsDetecting(true);
    
    // Try to get video element when playback starts
    if (!videoRef.current && playerRef.current) {
      setTimeout(() => {
        try {
          const internalPlayer = playerRef.current?.getInternalPlayer() as HTMLVideoElement;
          if (internalPlayer && internalPlayer.tagName === 'VIDEO') {
            videoRef.current = internalPlayer;
          }
        } catch (error) {
          console.warn('Could not get video element:', error);
        }
      }, 200);
    }
  };
  
  const handlePause = () => {
    setIsDetecting(false);
  };
  
  const handleEnded = () => {
    setIsDetecting(false);
  };
  
  const handleError = (error: any) => {
    console.error('Video error:', error);
    setVideoError('Failed to load video. Please check the video file exists.');
    setIsDetecting(false);
  };
  

  // Adjust video path to be relative to the public directory
  const adjustedPath = videoPath.replace('../', '/');
  
  // Log for debugging
  console.log('Video path:', adjustedPath);

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '800px' }}>
      <ReactPlayer
        ref={playerRef}
        url={adjustedPath}
        controls
        width="100%"
        height="auto"
        progressInterval={100}
        onProgress={handleProgress}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        onError={handleError}
        config={{
          file: {
            forceVideo: true
          }
        }}
      />
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
      {!isModelLoaded && !modelError && (
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
      
      {modelError && (
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
          <div style={{ marginTop: '10px', fontSize: '12px', opacity: 0.8 }}>
            You can test video paths at: <a href="/test-video.html" style={{ color: 'white' }}>/test-video.html</a>
          </div>
        </div>
      )}
      
      {isModelLoaded && !videoError && (
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
            <div style={{ fontSize: '10px', opacity: 0.7, display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <div>Video: {videoRef.current ? '✅' : '❌'}</div>
              <div>Path: {adjustedPath}</div>
            </div>
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

export default VideoPlayer;