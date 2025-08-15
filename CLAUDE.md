# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Urban Mobility Data Living Laboratory (UMDL2) - A comprehensive traffic monitoring platform providing both real-time browser-based and server-processed AI-powered traffic analysis for NYC intersections.

### Current Deployment
- **Frontend URL**: https://asdfghjklzxcvbnm.aimobilitylab.xyz/ (Auto-start: Systemd)
- **GitHub Pages**: https://ai-mobility-research-lab.github.io/UMDL2/ (Auto-deploy: GitHub Actions)
- **Backend API**: http://classificationbackend.boshang.online/ (Auto-start: Systemd)
- **Proxy Service**: FRP reverse proxy for public access (Auto-start: Systemd)
- **Auto-Start**: All services configured for automatic startup on Ubuntu reboot

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

# Docker Operations (Frontend Only)
docker-compose up -d frontend      # Start frontend service
docker-compose down               # Stop all services
docker logs umdl2-frontend        # View frontend logs

# Backend Management (Systemd Service)
sudo systemctl start umdl2-backend.service    # Start backend
sudo systemctl stop umdl2-backend.service     # Stop backend
sudo systemctl restart umdl2-backend.service  # Restart backend
sudo systemctl status umdl2-backend.service   # Check status
journalctl -u umdl2-backend.service -f        # View live logs
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

### Current Architecture
**Frontend**: Systemd Service (umdl2-frontend)
- **Service**: `umdl2-frontend.service` serving production build
- **Runtime**: Python HTTP server with optimized static file serving
- **Port**: 5173
- **Auto-start**: Systemd service (enabled)
- **Public Access**: via FRP proxy → https://asdfghjklzxcvbnm.aimobilitylab.xyz/

**Backend**: Python Virtual Environment + Systemd
- **Service**: `umdl2-backend.service` (systemd)
- **Runtime**: Python venv at `/backend/venv/bin/python`
- **Port**: 8001 (FastAPI + Uvicorn)
- **Auto-start**: Systemd service (enabled)
- **Public Access**: via FRP proxy → http://classificationbackend.boshang.online/

**Reverse Proxy**: FRP Client
- **Service**: `frpc.service` (systemd)
- **Config**: `/home/roboticslab/Downloads/frp_0.46.1_linux_amd64/frpc.ini`
- **Auto-start**: Systemd service (enabled)
- **Function**: Exposes local services to public domains

### Auto-Start Configuration

#### Services Enabled for Boot:
```bash
# Check auto-start status
systemctl is-enabled docker          # enabled (Docker Engine)
systemctl is-enabled umdl2-backend   # enabled (UMDL2 Backend API)
systemctl is-enabled frpc            # enabled (FRP Reverse Proxy)

# Docker containers with restart policies
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
# umdl2-frontend: restart=unless-stopped
```

#### Backend Systemd Service
```bash
# Service file: /etc/systemd/system/umdl2-backend.service
# Working Directory: /backend/
# Executable: /backend/venv/bin/python api_server.py
# User: roboticslab
# Auto-restart: 3-second delay on failure

# Service configuration details:
[Unit]
Description=UMDL2 Backend API Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=roboticslab
Group=roboticslab
WorkingDirectory=/home/roboticslab/City College Dropbox/BO SHANG/NYCDOT_classification_project/nyc-traffic-monitor/backend
ExecStart="/home/roboticslab/City College Dropbox/BO SHANG/NYCDOT_classification_project/nyc-traffic-monitor/backend/venv/bin/python" api_server.py --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Recovery After Reboot
All services automatically start in this order:
1. **Docker Engine** → starts `umdl2-frontend` container
2. **FRP Client** → establishes reverse proxy tunnels  
3. **UMDL2 Backend** → starts Python API server
4. **Services Ready** → Frontend and Backend accessible via public URLs

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

## Service Management

### Frontend Management (Systemd)
```bash
# Service operations
sudo systemctl status umdl2-frontend.service             # Check status
sudo systemctl start umdl2-frontend.service              # Start service
sudo systemctl stop umdl2-frontend.service               # Stop service
sudo systemctl restart umdl2-frontend.service            # Restart service

# Logs and monitoring
journalctl -u umdl2-frontend.service -f                  # Live logs
journalctl -u umdl2-frontend.service --since "1 hour ago" # Recent logs

# Rebuild production build after code changes
npm run build                                            # Rebuild static files
sudo systemctl restart umdl2-frontend.service            # Restart to serve new build

# Health checks
curl -s http://localhost:5173/ | head -10               # Test local access
curl -s https://asdfghjklzxcvbnm.aimobilitylab.xyz/      # Test public access
```

### Backend Management (Systemd)
```bash
# Service operations
sudo systemctl status umdl2-backend.service             # Check status
sudo systemctl start umdl2-backend.service              # Start service
sudo systemctl stop umdl2-backend.service               # Stop service
sudo systemctl restart umdl2-backend.service            # Restart service

# Logs and monitoring
journalctl -u umdl2-backend.service -f                  # Live logs
journalctl -u umdl2-backend.service --since "1 hour ago" # Recent logs

# Health checks
curl -s http://localhost:8001/health                     # Test local API
curl -s http://classificationbackend.boshang.online/health # Test public API
```

### FRP Proxy Management
```bash
# Service operations
sudo systemctl status frpc.service                      # Check proxy status
sudo systemctl restart frpc.service                     # Restart proxy
journalctl -u frpc.service --since "10 minutes ago"     # Check proxy logs

# Configuration
sudo nano /home/roboticslab/Downloads/frp_0.46.1_linux_amd64/frpc.ini  # Edit config
```

### Full System Recovery
```bash
# After reboot or system issues, restart all services:
sudo systemctl restart frpc.service                     # 1. Restart proxy
docker-compose up -d frontend                           # 2. Start frontend
sudo systemctl restart umdl2-backend.service            # 3. Restart backend

# Verify all services
sudo systemctl status frpc umdl2-backend docker         # Check service status
docker ps --filter "name=umdl2"                         # Check containers
curl -s http://asdfghjklzxcvbnm.aimobilitylab.xyz/       # Test frontend
curl -s http://classificationbackend.boshang.online/health # Test backend
```

## Troubleshooting

### Auto-Start Issues After Reboot
1. **Check enabled services**:
   ```bash
   systemctl is-enabled docker frpc umdl2-backend
   # All should show "enabled"
   ```
2. **Check service status**:
   ```bash
   systemctl status docker frpc umdl2-backend --no-pager
   ```
3. **Check Docker container auto-restart**:
   ```bash
   docker ps -a --filter "name=umdl2-frontend"
   # Status should be "Up" with restart policy "unless-stopped"
   ```

### Backend Not Starting (Systemd)
1. **Check service logs**:
   ```bash
   journalctl -u umdl2-backend.service --no-pager -l
   ```
2. **Common issues**:
   - Python virtual environment path problems
   - Working directory permissions
   - Port 8001 already in use
3. **Manual test**:
   ```bash
   cd backend && source venv/bin/activate && python api_server.py --port 8001
   ```

### Frontend Container Issues
1. **Check container status**:
   ```bash
   docker ps --filter "name=umdl2-frontend"
   docker logs umdl2-frontend --tail 20
   ```
2. **Common issues**:
   - Docker daemon not running
   - Port 5173 conflicts
   - Volume mounting problems
3. **Rebuild if needed**:
   ```bash
   docker-compose down
   docker-compose up -d frontend --build
   ```

### Public Access Issues
1. **Check FRP proxy**:
   ```bash
   systemctl status frpc.service
   journalctl -u frpc.service --since "5 minutes ago"
   ```
2. **Test local services first**:
   ```bash
   curl http://localhost:5173/  # Frontend should return HTML
   curl http://localhost:8001/health  # Backend should return JSON
   ```
3. **Check FRP configuration**:
   ```bash
   grep -A 3 "classification_tmp-http\|classificationbackend-http" /home/roboticslab/Downloads/frp_0.46.1_linux_amd64/frpc.ini
   ```

### Docker Socket Issues
1. **Set correct Docker socket**:
   ```bash
   export DOCKER_HOST=unix:///var/run/docker.sock
   echo 'export DOCKER_HOST=unix:///var/run/docker.sock' >> ~/.bashrc
   ```
2. **Check Docker daemon**:
   ```bash
   sudo systemctl status docker
   sudo usermod -aG docker roboticslab  # Add user to docker group
   ```

### Video Playback Issues
1. Test with direct URL: `http://localhost:5173/test-video.html`
2. Check video codec compatibility (H.264 recommended)
3. Verify file permissions in Docker volumes
4. Look for CSP errors in browser console
5. Check processed videos exist: `ls backend/processed_videos/`

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
- **August 2025**: Resolved Docker Desktop conflicts preventing auto-start
- **August 2025**: Configured backend as systemd service for reliable auto-start
- **August 2025**: Fixed FRP proxy reconnection after service restarts

## Development Best Practices

1. **Always check location ID consistency** between frontend and backend
2. **Test API endpoints** before assuming frontend issues
3. **Monitor service logs** for health:
   - Frontend: `docker logs umdl2-frontend`
   - Backend: `journalctl -u umdl2-backend.service -f`
   - FRP: `journalctl -u frpc.service -f`
4. **Use test scripts** (`test-processed-videos.sh`) to verify setup
5. **Clear browser cache** when testing frontend changes
6. **Restart services** after configuration changes:
   - Frontend: `docker restart umdl2-frontend`
   - Backend: `sudo systemctl restart umdl2-backend.service`
   - FRP: `sudo systemctl restart frpc.service`
7. **Verify auto-start configuration** after system changes:
   - `systemctl is-enabled docker frpc umdl2-backend`
   - `docker ps --filter "name=umdl2"`
8. **Test public accessibility** after service restarts:
   - Frontend: http://asdfghjklzxcvbnm.aimobilitylab.xyz/
   - Backend: http://classificationbackend.boshang.online/health

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
- Always make sure the video is web-compatible.