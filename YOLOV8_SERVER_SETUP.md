# YOLOv8 Server-Side Processing Setup

## Overview
This document describes the server-side YOLOv8 implementation for processing NYC traffic videos with transportation-specific object detection.

## Architecture

### Components
1. **FastAPI Backend** (`backend/app/main.py`)
   - REST API for video processing
   - Static file serving for processed videos
   - Background task processing

2. **Video Processor** (`backend/app/video_processor.py`)
   - YOLOv8 model integration
   - Frame-by-frame detection
   - Bounding box drawing
   - Video export with overlays

3. **Enhanced Frontend** (`src/components/VideoPlayerEnhanced.tsx`)
   - Toggle between live detection and pre-processed videos
   - Automatic detection of processed videos
   - On-demand processing trigger

## Installation

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Process Videos (One-time)
```bash
cd backend
python process_videos.py
```
This will process all three intersection videos and save them with bounding boxes.

### 3. Start Servers
```bash
# Option 1: Use the startup script
./run_servers.sh

# Option 2: Run manually
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
npm run dev
```

## API Endpoints

### Health Check
```
GET http://localhost:8001/health
```
Returns model status and server health.

### Process Single Video
```
POST http://localhost:8001/process-video
Body: {
  "location_id": "74th–Amsterdam–Columbus",
  "video_filename": "2025-02-13_06-00-04.mp4"
}
```
Triggers background processing of a specific video.

### Process All Videos
```
POST http://localhost:8001/process-all-videos
```
Processes all three intersection videos in the background.

### Check Processing Status
```
GET http://localhost:8001/processing-status/{location_id}
```
Returns status and file paths for processed videos.

### List Processed Videos
```
GET http://localhost:8001/list-processed-videos
```
Returns all available processed videos.

### Serve Processed Video
```
GET http://localhost:8001/processed/{filename}
```
Streams the processed video file.

## Usage in Web App

### Automatic Detection
The VideoPlayerEnhanced component automatically:
1. Checks for processed videos on mount
2. Shows toggle if processed video exists
3. Allows switching between live and processed

### Manual Processing
If no processed video exists:
1. Click "Process with YOLOv8" button
2. Wait for processing (shown in console)
3. Toggle will become available when done

### Performance Comparison

| Mode | FPS | Accuracy | CPU Usage | GPU Usage |
|------|-----|----------|-----------|-----------|
| Browser (COCO-SSD) | 10-20 | Medium | High | N/A |
| Server (YOLOv8) | 30-60 | High | Low | High |

## Model Information

The system uses a fine-tuned YOLOv8 model located at:
```
/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt
```

This model is specifically trained for transportation objects:
- Cars
- Trucks
- Buses
- Motorcycles
- Bicycles
- Pedestrians

## Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server
│   └── video_processor.py   # YOLOv8 processing
├── processed_videos/         # Output directory
├── requirements.txt         # Python dependencies
└── process_videos.py        # Batch processing script

src/components/
├── VideoPlayerEnhanced.tsx  # Enhanced player with toggle
└── VideoPlayerNative.tsx    # Original player (fallback)
```

## Troubleshooting

### Model Not Loading
- Verify model path exists: `/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt`
- Check CUDA/GPU availability: `python -c "import torch; print(torch.cuda.is_available())"`

### Video Processing Fails
- Check video files exist in `public/` directory
- Verify OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`
- Check disk space for processed videos

### CORS Issues
- Ensure backend is running on port 8001
- Frontend should be on port 5173
- Check CORS settings in `backend/app/main.py`

### Performance Issues
- Reduce confidence threshold (default: 0.3)
- Process videos offline instead of real-time
- Use GPU acceleration if available

## Next Steps

1. **Batch Processing**: Set up cron job for automatic processing
2. **WebSocket Streaming**: Real-time detection results
3. **Cloud Deployment**: Deploy to AWS/Azure for scalability
4. **Model Fine-tuning**: Improve accuracy on NYC-specific traffic