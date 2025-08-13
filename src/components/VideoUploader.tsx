import React, { useState, useRef } from 'react';

interface VideoUploaderProps {
  onVideoUpload: (file: File, customLocation: string) => void;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({ onVideoUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [customLocation, setCustomLocation] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const videoFile = files.find(file => file.type.startsWith('video/'));
    
    if (videoFile) {
      handleFileUpload(videoFile);
    } else {
      alert('Please upload a valid video file (MP4, WebM, AVI, MOV, etc.)');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!customLocation.trim()) {
      alert('Please enter a location name for this video');
      return;
    }

    if (file.size > 500 * 1024 * 1024) { // 500MB limit
      alert('File size is too large. Please upload videos smaller than 500MB.');
      return;
    }

    setIsUploading(true);
    try {
      onVideoUpload(file, customLocation.trim());
      setCustomLocation('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="video-uploader">
      <h3>Upload Custom Video</h3>
      
      <div className="location-input-section">
        <label htmlFor="location-input">Location Name:</label>
        <input
          id="location-input"
          type="text"
          placeholder="e.g., Main St & Oak Ave"
          value={customLocation}
          onChange={(e) => setCustomLocation(e.target.value)}
          className="location-input"
          disabled={isUploading}
        />
      </div>

      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isUploading}
        />
        
        <div className="upload-content">
          {isUploading ? (
            <>
              <div className="upload-spinner">⏳</div>
              <p>Processing video...</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📹</div>
              <p><strong>Click to select</strong> or drag and drop a video file</p>
              <p className="upload-hint">Supports MP4, WebM, AVI, MOV (max 500MB)</p>
            </>
          )}
        </div>
      </div>

      <style jsx>{`
        .video-uploader {
          margin: 20px 0;
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: #f9f9f9;
        }

        .location-input-section {
          margin-bottom: 15px;
        }

        .location-input-section label {
          display: block;
          margin-bottom: 5px;
          font-weight: bold;
          color: #333;
        }

        .location-input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-size: 14px;
        }

        .location-input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .upload-zone {
          border: 2px dashed #ccc;
          border-radius: 8px;
          padding: 40px 20px;
          text-align: center;
          cursor: pointer;
          transition: all 0.3s ease;
          background: white;
        }

        .upload-zone:hover {
          border-color: #007bff;
          background: #f8f9fa;
        }

        .upload-zone.dragging {
          border-color: #007bff;
          background: #e7f3ff;
          transform: scale(1.02);
        }

        .upload-zone.uploading {
          cursor: not-allowed;
          opacity: 0.7;
        }

        .upload-content {
          pointer-events: none;
        }

        .upload-icon {
          font-size: 48px;
          margin-bottom: 10px;
        }

        .upload-spinner {
          font-size: 48px;
          margin-bottom: 10px;
          animation: spin 2s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .upload-zone p {
          margin: 5px 0;
          color: #666;
        }

        .upload-hint {
          font-size: 12px;
          color: #888;
        }
      `}</style>
    </div>
  );
};

export default VideoUploader;