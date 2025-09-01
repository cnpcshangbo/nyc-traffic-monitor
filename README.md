# Urban Mobility Data Living Laboratory (UMDL2)

A comprehensive traffic monitoring platform providing AI-powered traffic analysis for NYC intersections using both real-time browser-based and server-processed object detection.

🌐 **Live Demo**: https://asdfghjklzxcvbnm.aimobilitylab.xyz/

## Features

- 🎯 **Dual Processing Modes**: Toggle between YOLOv8 server-processed and browser-based COCO-SSD detection
- 🗺️ **Interactive Map**: Real-time traffic monitoring at Staten Island and Bronx intersections
- 📊 **Live Analytics**: Traffic volume charts synchronized with video playback
- 💾 **Data Export**: CSV/XLSX export with configurable time aggregation
- 📹 **Video Upload**: Custom video processing with drag-and-drop interface
- 🚀 **High Performance**: Server-side YOLOv8 processing for better accuracy

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Ubuntu 22.04+ (for production deployment)

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd nyc-traffic-monitor
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
# Frontend available at http://localhost:5173
```

4. **Start backend API** (optional, for processed videos)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
# API available at http://localhost:8001
```

## Production Deployment

### Using Docker Compose

1. **Build and start services**
```bash
docker-compose up -d
```

2. **Check service status**
```bash
docker ps
docker logs umdl2-frontend
```

3. **Enable auto-restart on reboot**
```bash
sudo cp umdl2.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable umdl2.service
sudo systemctl start umdl2.service
```

### Manual Backend Deployment

1. **Start API server**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

2. **Process videos with YOLOv8**
```bash
python process_videos.py
```

## Architecture

### Frontend Stack
- React 18 + TypeScript + Vite
- TensorFlow.js for browser-side detection
- Leaflet for interactive mapping
- Recharts for data visualization

### Backend Stack
- FastAPI for REST API
- YOLOv8 for server-side detection
- OpenCV for video processing
- Docker for containerization

### Data Flow
```
User Selection → Video Player → Detection Engine → Analytics → Export
                      ↓                ↓
              Processed Video    Live Detection
                (YOLOv8)         (TensorFlow.js)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/processing-status/{location_id}` | GET | Check for processed videos |
| `/process-video` | POST | Trigger YOLOv8 processing |
| `/processed/{filename}` | GET/HEAD/OPTIONS | Serve processed video with range support |
| `/videos/{filename}` | GET/HEAD/OPTIONS | Serve original video with range support |
| `/list-processed-videos` | GET | List all processed videos |

### Legacy Backend (api_server.py)
Some frontend views (e.g., fetching `/locations`) were designed against the legacy backend entrypoint `backend/api_server.py`. If you run that server instead of `app.main`, these routes are available:

- `GET /locations` — Lists locations with original/processed availability
- `GET /processed-videos/{filename}` — Serves processed videos (no range support)
- `GET /videos/{filename}` — Serves original videos

Run legacy server:
```bash
cd backend
python api_server.py --host 0.0.0.0 --port 8001 --reload
```
If using `app.main`, implement an equivalent `/locations` route or adjust the frontend to not require it.

## Configuration

### Environment Variables
```bash
# Frontend
VITE_API_URL=http://localhost:8001  # API backend URL

# Backend
MODEL_PATH=/path/to/yolov8/best.pt   # YOLOv8 weights (overrides default)
PROCESSED_VIDEOS_DIR=/app/processed_videos
ORIGINAL_VIDEOS_DIR=/app/public
```

Defaults (if unset):
- `MODEL_PATH`: `/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt`
- `PROCESSED_VIDEOS_DIR`: `backend/processed_videos`
- `ORIGINAL_VIDEOS_DIR`: `backend/../public`

Examples:
- Frontend: create `.env.local` → `VITE_API_URL=http://localhost:8001`
- Backend: `MODEL_PATH=/models/best.pt PROCESSED_VIDEOS_DIR=/data/processed ORIGINAL_VIDEOS_DIR=/data/public uvicorn app.main:app --host 0.0.0.0 --port 8001`

### Location Configuration
Locations are defined in `src/App.tsx`:
- **Richmond Hill Rd & Edinboro Rd, Staten Island**
- **Arthur Kill Rd & Storer Ave, Staten Island**
- **Katonah Ave & East 241st St, Bronx**

## Testing

### Run Tests
```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest

# API test
./test-processed-videos.sh
```

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## Troubleshooting

### Common Issues

**Processed videos not showing?**
- Check API health: `curl http://localhost:8001/health`
- Verify location IDs match (case-sensitive)
- Ensure processed video files exist in `backend/processed_videos/`

**Frontend not updating?**
- Restart Docker container: `docker restart umdl2-frontend`
- Clear browser cache
- Check for HMR updates in console

**API connection errors?**
- Verify backend is running
- Check CORS configuration
- Ensure correct API URL via `VITE_API_URL` (see `.env.local`)

## Development

### Project Structure
```
nyc-traffic-monitor/
├── src/                    # Frontend source code
│   ├── components/         # React components
│   ├── services/          # Detection services
│   └── config/            # Configuration files
├── backend/               # Backend API
│   ├── api_server.py      # FastAPI server
│   ├── process_videos.py  # YOLOv8 processing
│   └── processed_videos/  # Processed video storage
├── public/                # Static assets and videos
├── docker-compose.yml     # Docker configuration
└── CLAUDE.md             # AI assistant documentation
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is part of the NYC Department of Transportation traffic monitoring initiative.

## Support

For issues and questions:
- Check [CLAUDE.md](./CLAUDE.md) for detailed documentation
- Review [troubleshooting guide](#troubleshooting)
- Open an issue on GitHub

---

**Current Version**: 2.0.0 (UMDL2)  
**Last Updated**: August 2025  
**Maintained by**: AI Mobility Lab
