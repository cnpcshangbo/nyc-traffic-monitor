# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NYC Department of Transportation (NYCDOT) traffic classification project - a React/TypeScript web application providing real-time AI-powered traffic analysis using TensorFlow.js on video feeds from NYC intersections.

### Core Features
- Interactive Leaflet map showing 3 NYC intersection locations (74th-Amsterdam-Columbus, Amsterdam-80th, Columbus-86th)
- Video playback with real-time COCO-SSD object detection and bounding box overlay
- Live traffic volume charts (Recharts) synchronized with video playback
- CSV export functionality with configurable aggregation levels
- Performance controls: adjustable detection interval (100-2000ms) and confidence threshold

## Development Commands

```bash
npm install          # Install dependencies
npm run dev          # Start Vite development server (http://localhost:5173)
npm run build        # TypeScript compilation + Vite production build
npm run preview     # Preview production build
npm run lint         # Run ESLint checks
npx tsc --noEmit     # TypeScript type checking only (no emit)
```

## Architecture Overview

### Technology Stack
- **Frontend Framework**: React 18 + TypeScript 5.6 + Vite 5.4
- **Object Detection**: TensorFlow.js with COCO-SSD model (CPU backend for CSP compatibility)
- **Mapping**: Leaflet.js with React Leaflet
- **Charts**: Recharts for real-time visualization
- **Video Processing**: Native HTML5 video with canvas overlay for bounding boxes
- **Data Export**: XLSX library for Excel export

### Key Components
- `src/App.tsx`: Main application component with location state management
- `src/components/MapView.tsx`: Interactive Leaflet map with location markers
- `src/components/VideoPlayerNative.tsx`: Primary video player with object detection and bounding box overlay
- `src/components/VideoPlayer.tsx`: Alternative ReactPlayer implementation (has CSP issues)
- `src/components/TrafficChart.tsx`: Real-time traffic volume visualization
- `src/services/objectDetection.ts`: TensorFlow.js COCO-SSD service for traffic detection
- `src/utils/analyzeExcel.ts`: Excel data analysis utility

### Object Detection Service
The `ObjectDetectionService` class handles:
- Model initialization with COCO-SSD
- Real-time object detection on video frames
- Traffic class mapping (cars, trucks, buses, motorcycles, bicycles, pedestrians)
- Detection history management for time-series analysis
- Aggregated traffic counts with configurable time intervals

### Data Flow
1. User selects location from map → Updates `selectedLocation` state
2. VideoPlayerNative loads corresponding video from `public/{location}/` directory
3. Object detection runs at configured interval → Detections stored with timestamps
4. TrafficChart displays real-time counts aggregated from detection history
5. Export functionality generates XLSX with time-aggregated traffic counts

## Configuration Details

### TypeScript Configuration
- **Target**: ES2020 with DOM libraries
- **Strict Mode**: Enabled with `noUnusedLocals` and `noUnusedParameters`
- **Module Resolution**: Bundler mode for Vite compatibility
- **Project References**: Split between `tsconfig.app.json` and `tsconfig.node.json`

### Vite Configuration
- **Asset Handling**: MP4 videos included via `assetsInclude: ['**/*.mp4']`
- **Plugin**: React with SWC for fast refresh
- **Server**: Default port 5173 with HMR

### ESLint Configuration
- **Format**: Modern flat config (`eslint.config.js`)
- **Plugins**: React Hooks, React Refresh, TypeScript ESLint
- **Ignored**: `dist/` directory

## Video and Data Structure

### Video Files Location
```
public/
├── 74th-Amsterdam-Columbus/
│   └── 2025-02-13_06-00-04.mp4
├── Amsterdam-80th/
│   └── 2025-02-13_06-00-04.mp4
└── Columbus-86th/
    └── 2025-02-13_06-00-06.mp4
```

### Detection Data Format
```typescript
interface Detection {
  bbox: [x, y, width, height];
  class: string;  // "car", "truck", "bus", etc.
  score: number;   // Confidence 0-1
  timestamp: number;
}
```

## Performance Considerations

### Current Implementation (Browser-side)
- Uses CPU backend to avoid CSP `unsafe-eval` issues
- Typical performance: 10-20 FPS on decent hardware
- Memory usage: 2-4GB browser limit
- Detection interval adjustable: 100-2000ms

### Future Server-side Implementation (See YOLOV8_IMPLEMENTATION_PLAN.md)
- YOLOv8 model for better accuracy
- GPU acceleration (100-500 FPS)
- Batch processing capabilities
- No browser memory constraints

## Troubleshooting

### Video Not Playing
1. Check test page: http://localhost:5173/test-video.html
2. Verify video files exist in `public/{location}/` directories
3. Check browser console for CORS/CSP errors

### Object Detection Issues
1. Model loading takes 2-5 seconds on first load
2. Ensure video element is rendered before detection starts
3. Adjust detection interval for better performance
4. Check confidence threshold settings

### CSP Issues
- App uses `VideoPlayerNative.tsx` to avoid ReactPlayer CSP issues
- TensorFlow.js configured for CPU backend (no eval required)
- For WebGL performance, would need `unsafe-eval` in CSP

## Current Branch Context

Working on `feature/transportation-yolov8-model` branch to implement YOLOv8 model for improved transportation-specific detection. Main development branch is `feature/realtime-browser-yolo-detection`.