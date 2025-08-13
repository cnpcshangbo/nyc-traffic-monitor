# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Urban Mobility Data Living Laboratory (UMDL2) - A comprehensive traffic monitoring platform providing both real-time browser-based and server-processed AI-powered traffic analysis for NYC intersections.

### Current Deployment
- **Frontend URL**: https://asdfghjklzxcvbnm.aimobilitylab.xyz/
- **Backend API**: http://classificationbackend.boshang.online/
- **Proxy Service**: FRP reverse proxy for public access

### Core Features
- **Dual Processing Modes**: Toggle between server-processed (YOLOv8) and browser-based (COCO-SSD) detection
- **Interactive Map**: Leaflet map showing 3 Staten Island/Bronx locations
- **Real-time Detection**: Live object detection with bounding box overlay
- **Traffic Analytics**: Live charts synchronized with video playback
- **Data Export**: CSV/XLSX export with configurable aggregation (15s, 30s, 5min, 15min)
- **Custom Schemas**: User-definable classification schemas for different analysis needs
- **Video Upload**: Support for custom video uploads and processing

### Current Locations (Updated)
1. **Richmond Hill Rd & Edinboro Rd, Staten Island** (ID: 74th-Amsterdam-Columbus)
2. **Arthur Kill Rd & Storer Ave, Staten Island** (ID: Amsterdam-80th)
3. **Katonah Ave & East 241st St, Bronx** (ID: Columbus-86th)

## Development Commands

```bash
# Frontend Development
npm install          # Install dependencies
npm run dev          # Start Vite dev server (http://localhost:5173)
npm run build        # Production build
npm run preview     # Preview production build
npm run lint         # Run ESLint checks
npx tsc --noEmit     # TypeScript type checking

# Backend Development
cd backend
source venv/bin/activate  # Activate Python virtual environment
python api_server.py --reload  # Run API server (port 8001)
python process_videos.py  # Process videos with YOLOv8

# Docker Operations
docker-compose up -d      # Start all services
docker-compose down       # Stop all services
docker logs umdl2-frontend  # View frontend logs
docker logs umdl2-backend   # View backend logs (when enabled)
```

## Architecture Overview

### Technology Stack

#### Frontend
- **Framework**: React 18 + TypeScript 5.6 + Vite 5.4
- **UI Components**: 
  - VideoPlayerEnhanced (dual-mode video player)
  - MapView (Leaflet integration with home button)
  - TrafficChart (Recharts visualization)
  - ProcessingProgress (server processing status)
  - VideoUploader (drag-and-drop uploads)
- **AI Models**: TensorFlow.js with COCO-SSD (browser-side)
- **State Management**: React hooks + refs

#### Backend
- **API Framework**: FastAPI with Uvicorn
- **AI Model**: YOLOv8 for server-side processing
- **Video Processing**: OpenCV + FFmpeg
- **File Storage**: Local filesystem with processed_videos directory

### Key Components

#### Frontend Components
- `src/App.tsx`: Main app with location management and auto-scroll
- `src/components/VideoPlayerEnhanced.tsx`: Dual-mode video player supporting both processed and live detection
- `src/components/MapView.tsx`: Interactive map with location markers and home button
- `src/components/ProcessingProgress.tsx`: Real-time server processing status
- `src/components/VideoUploader.tsx`: Drag-and-drop video upload interface
- `src/services/objectDetection.ts`: TensorFlow.js COCO-SSD service
- `src/config/api.ts`: API endpoint configuration with environment detection

#### Backend Components
- `backend/api_server.py`: FastAPI server for processed videos and API endpoints
- `backend/process_videos.py`: YOLOv8 video processing script
- `backend/processed_videos/`: Storage for YOLOv8-processed videos

### Data Flow

#### Live Detection Mode
1. User selects location → VideoPlayerEnhanced loads original video
2. TensorFlow.js COCO-SSD model initializes in browser
3. Real-time detection on canvas overlay at configured interval
4. TrafficChart displays live aggregated counts
5. Export generates CSV with time-based aggregation

#### Server-Processed Mode
1. User selects location → API checks for processed video
2. If available, loads YOLOv8-processed video with embedded bounding boxes
3. No browser AI computation needed - better performance
4. Higher accuracy with transportation-specific YOLOv8 model

## API Configuration

### Environment-based API URLs
```typescript
// src/config/api.ts
- Local development: http://localhost:8001
- Public domain (asdfghjklzxcvbnm.aimobilitylab.xyz): http://classificationbackend.boshang.online
- Classification domain: http://classificationbackend.boshang.online
```

### API Endpoints
- `GET /health`: Health check
- `GET /processing-status/{location_id}`: Check for processed videos
- `POST /process-video`: Trigger YOLOv8 processing
- `GET /processed-videos/{filename}`: Serve processed video files
- `GET /locations`: List all locations with processing status

## Deployment Configuration

### Docker Compose Setup
- **Frontend Container**: Vite dev server on port 5173
- **Backend Container**: FastAPI server on port 8001 (optional)
- **Network**: umdl2-network bridge
- **Volumes**: Mounted source code for hot-reload

### Systemd Service (Auto-restart)
```bash
# Service file: /etc/systemd/system/umdl2.service
sudo systemctl enable umdl2.service  # Enable auto-start
sudo systemctl start umdl2.service   # Start service
sudo systemctl status umdl2.service  # Check status
```

### Important Configuration Notes

#### Location ID Case Sensitivity
Location IDs must match exactly between frontend and backend:
- ✅ Correct: `74th-Amsterdam-Columbus` (mixed case)
- ❌ Wrong: `74th-amsterdam-columbus` (lowercase)

#### CORS Configuration
Backend allows all origins (`*`) for development. In production, specify actual domains.

#### Video Path Structure
- Original videos: `public/{location-id}/*.mp4`
- Processed videos: `backend/processed_videos/{location-id}_*_processed.mp4`

## Performance Optimization

### Browser-side (TensorFlow.js)
- CPU backend to avoid CSP issues
- 10-20 FPS typical performance
- Adjustable detection interval (100-2000ms)
- Confidence threshold filtering (0.1-0.9)

### Server-side (YOLOv8)
- GPU acceleration when available
- Pre-processed videos with embedded bounding boxes
- No browser computation required
- Higher accuracy for transportation objects

## Troubleshooting

### Processed Videos Not Showing
1. Check API is accessible: `curl http://classificationbackend.boshang.online/health`
2. Verify location IDs match (case-sensitive)
3. Ensure backend service is running: `docker logs umdl2-backend`
4. Check processed video files exist: `ls backend/processed_videos/`

### Frontend Not Updating
1. Docker container may have cached code: `docker restart umdl2-frontend`
2. Clear browser cache and hard refresh
3. Check HMR is working: Look for `[vite] hmr update` in console

### API Connection Issues
1. Verify backend is running: `systemctl status api_server` or check Docker
2. Test API directly: `curl http://localhost:8001/health`
3. Check CORS errors in browser console
4. Ensure frp proxy is configured for port 8001

### Video Playback Issues
1. Test with direct URL: `http://localhost:5173/test-video.html`
2. Check video codec compatibility (H.264 recommended)
3. Verify file permissions in Docker volumes
4. Look for CSP errors in browser console

## Recent Updates (August 2025)

### Major Changes
1. **Rebranded to UMDL2**: Urban Mobility Data Living Laboratory
2. **Added YOLOv8 Backend**: Server-side processing with higher accuracy
3. **Dual-mode Video Player**: Toggle between processed and live detection
4. **Updated Locations**: Changed to Staten Island and Bronx intersections
5. **API Integration**: Backend accessible via classificationbackend.boshang.online
6. **Auto-scroll UX**: Automatic scroll to video when location selected
7. **Home Button**: Easy map navigation to view all locations
8. **Processing Progress**: Live status for server-side video processing

### Bug Fixes
- Fixed location ID case sensitivity issue
- Resolved API URL configuration for public access
- Fixed Docker socket configuration conflicts
- Corrected systemd service for auto-restart
- Updated frontend to use correct location IDs

## Development Best Practices

1. **Always check location ID consistency** between frontend and backend
2. **Test API endpoints** before assuming frontend issues
3. **Monitor Docker logs** for container health
4. **Use test scripts** (`test-processed-videos.sh`) to verify setup
5. **Clear browser cache** when testing frontend changes
6. **Restart containers** after configuration changes
7. **Check backend logs** for API call patterns and errors

## Security Considerations

- Passwordless sudo configured for roboticslab user (development only)
- CORS currently allows all origins (restrict in production)
- No authentication on API endpoints (add in production)
- Video files publicly accessible (consider access control)

## Future Enhancements

See `YOLOV8_IMPLEMENTATION_PLAN.md` for detailed roadmap including:
- Real-time streaming support
- Multi-camera synchronization
- Advanced analytics dashboard
- Cloud storage integration
- Authentication and user management