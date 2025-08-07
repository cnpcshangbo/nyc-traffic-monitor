# Branch: feature/realtime-browser-yolo-detection

## Overview

This branch contains the real-time browser-based YOLO object detection implementation for the NYC Traffic Monitor project.

## Key Features

- **Real-time Processing**: All object detection runs directly in the browser using TensorFlow.js
- **COCO-SSD Model**: Pre-trained model for detecting vehicles and pedestrians
- **WebGL Acceleration**: Uses GPU via WebGL for faster inference
- **Live Bounding Boxes**: Real-time overlay of detection results on video
- **No Server Required**: Completely client-side processing

## Technical Implementation

### Object Detection
- TensorFlow.js with COCO-SSD model
- Detects: cars, trucks, buses, motorcycles, bicycles, pedestrians
- Configurable detection interval (100ms - 2000ms)
- Adjustable confidence threshold (10% - 90%)

### Performance Optimizations
- RequestAnimationFrame for smooth rendering
- Throttled detection to reduce CPU usage
- Efficient canvas drawing for bounding boxes
- Native HTML5 video element (VideoPlayerNative)

## Known Limitations

1. **Browser Performance**: Limited by client hardware
2. **Memory Usage**: Large video files and model in memory
3. **Battery Drain**: High power consumption on mobile
4. **CSP Requirements**: Needs 'unsafe-eval' for TensorFlow.js

## Why This Approach?

This implementation demonstrates:
- Feasibility of browser-based traffic analysis
- Real-time visualization capabilities
- No infrastructure requirements
- Easy deployment and testing

However, for production use, offline processing is recommended for better performance and accuracy.

## Files Specific to This Implementation

- `src/components/VideoPlayerNative.tsx` - Native video player with detection
- `src/services/objectDetection.ts` - TensorFlow.js integration
- `src/components/TrafficChart.tsx` - Real-time chart updates
- CSP configuration in `index.html`

## Running This Version

```bash
npm install
npm run dev
```

Note: Ensure your browser supports WebGL for optimal performance.