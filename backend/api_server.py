#!/usr/bin/env python3
"""
FastAPI backend server for serving processed videos and handling processing requests.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="NYC Traffic Monitor API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = Path(__file__).parent
PROCESSED_VIDEOS_DIR = BASE_DIR / "processed_videos"
ORIGINAL_VIDEOS_DIR = BASE_DIR.parent / "public"

# Ensure directories exist
PROCESSED_VIDEOS_DIR.mkdir(exist_ok=True)

# Location mapping for file naming consistency
LOCATION_MAP = {
    "74th-Amsterdam-Columbus": {
        "name": "Richmond Hill Road & Edinboro Rd, Staten Island",
        "video_file": "2025-02-13_06-00-04.mp4"
    },
    "Amsterdam-80th": {
        "name": "Arthur Kill Rd & Storer Ave, Staten Island", 
        "video_file": "2025-02-13_06-00-04.mp4"
    },
    "Columbus-86th": {
        "name": "Katonah Ave & East 241st St, Bronx",
        "video_file": "2025-02-13_06-00-06.mp4"
    }
}

class ProcessVideoRequest(BaseModel):
    location_id: str
    video_filename: str

class ProcessingStatus(BaseModel):
    status: str  # "not_found", "processing", "completed", "error"
    files: List[str]
    message: Optional[str] = None

# In-memory processing status tracker
processing_status: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "NYC Traffic Monitor API"}

@app.get("/processing-status/{location_id}", response_model=ProcessingStatus)
async def get_processing_status(location_id: str):
    """Get processing status for a specific location."""
    
    # Check if processed video file exists
    processed_files = []
    for file in PROCESSED_VIDEOS_DIR.glob(f"{location_id}_*_processed.mp4"):
        processed_files.append(f"/processed-videos/{file.name}")
    
    if processed_files:
        return ProcessingStatus(
            status="completed",
            files=processed_files,
            message=f"Found {len(processed_files)} processed video(s)"
        )
    
    # Check if currently processing
    if location_id in processing_status:
        status_info = processing_status[location_id]
        return ProcessingStatus(
            status=status_info["status"],
            files=[],
            message=status_info.get("message", "Processing in progress")
        )
    
    return ProcessingStatus(
        status="not_found",
        files=[],
        message="No processed video found"
    )

@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, background_tasks: BackgroundTasks):
    """Trigger video processing with YOLOv8."""
    
    location_id = request.location_id
    
    # Check if already processed
    processed_files = list(PROCESSED_VIDEOS_DIR.glob(f"{location_id}_*_processed.mp4"))
    if processed_files:
        return {
            "status": "already_processed",
            "output_path": f"/processed-videos/{processed_files[0].name}",
            "message": "Video already processed"
        }
    
    # Check if currently processing
    if location_id in processing_status and processing_status[location_id]["status"] == "processing":
        return {
            "status": "processing",
            "message": "Video is already being processed"
        }
    
    # Check if source video exists
    source_video_path = ORIGINAL_VIDEOS_DIR / location_id / request.video_filename
    if not source_video_path.exists():
        raise HTTPException(status_code=404, detail=f"Source video not found: {source_video_path}")
    
    # Mark as processing
    processing_status[location_id] = {
        "status": "processing",
        "message": "Processing started"
    }
    
    # Start background processing
    background_tasks.add_task(run_video_processing, location_id, str(source_video_path))
    
    return {
        "status": "processing",
        "message": "Video processing started"
    }

async def run_video_processing(location_id: str, input_video_path: str):
    """Run video processing in the background."""
    try:
        # Activate virtual environment and run processing script
        venv_python = BASE_DIR / "venv" / "bin" / "python"
        process_script = BASE_DIR / "process_videos.py"
        
        cmd = [
            str(venv_python),
            str(process_script),
            input_video_path,
            "--location_id", location_id
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(BASE_DIR)
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            processing_status[location_id] = {
                "status": "completed",
                "message": "Processing completed successfully"
            }
        else:
            processing_status[location_id] = {
                "status": "error",
                "message": f"Processing failed: {stderr.decode()}"
            }
            
    except Exception as e:
        processing_status[location_id] = {
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        }

# Mount static files for processed videos
app.mount("/processed-videos", StaticFiles(directory=str(PROCESSED_VIDEOS_DIR)), name="processed-videos")

@app.get("/processed-videos/{filename}")
async def get_processed_video(filename: str):
    """Serve processed video files."""
    file_path = PROCESSED_VIDEOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Processed video not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=filename
    )

@app.get("/locations")
async def get_locations():
    """Get available locations and their processing status."""
    locations = []
    
    for location_id, info in LOCATION_MAP.items():
        # Check for processed videos
        processed_files = list(PROCESSED_VIDEOS_DIR.glob(f"{location_id}_*_processed.mp4"))
        
        locations.append({
            "id": location_id,
            "name": info["name"],
            "original_video": info["video_file"],
            "has_processed": len(processed_files) > 0,
            "processed_files": [f.name for f in processed_files]
        })
    
    return {"locations": locations}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NYC Traffic Monitor API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"Starting NYC Traffic Monitor API server on {args.host}:{args.port}")
    print(f"Processed videos directory: {PROCESSED_VIDEOS_DIR}")
    print(f"Original videos directory: {ORIGINAL_VIDEOS_DIR}")
    
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        access_log=True
    )