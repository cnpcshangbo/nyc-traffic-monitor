from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import os
import logging
from pathlib import Path
from .video_processor import VideoProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Urban Mobility Data Living Laboratory (UMDL2) - YOLOv8 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://classification.boshang.online",
        "https://classification.boshang.online",
        "http://asdfghjklzxcvbnm.aimobilitylab.xyz",
        "https://asdfghjklzxcvbnm.aimobilitylab.xyz"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt",
)

# Allow overriding IO dirs via env
PROCESSED_VIDEOS_DIR = Path(os.getenv("PROCESSED_VIDEOS_DIR", "processed_videos"))
PROCESSED_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
ORIGINAL_VIDEOS_DIR = Path(os.getenv("ORIGINAL_VIDEOS_DIR", "../public"))

video_processor = VideoProcessor(MODEL_PATH)

# Custom route for serving processed videos with proper encoding
import urllib.parse

# Known demo locations (stub for parity with legacy api_server.py)
LOCATIONS = [
    {"id": "74th-Amsterdam-Columbus", "name": "Richmond Hill Road & Edinboro Rd, Staten Island", "filename": "2025-02-13_06-00-04.mp4"},
    {"id": "Amsterdam-80th", "name": "Arthur Kill Rd & Storer Ave, Staten Island", "filename": "2025-02-13_06-00-04.mp4"},
    {"id": "Columbus-86th", "name": "Katonah Ave & East 241st St, Bronx", "filename": "2025-02-13_06-00-06.mp4"},
]

@app.get("/processed/{filename:path}")
@app.head("/processed/{filename:path}")
@app.options("/processed/{filename:path}")
async def serve_processed_video(filename: str, request: Request):
    """Serve processed video files with proper range request handling"""
    try:
        # URL decode the filename
        decoded_filename = urllib.parse.unquote(filename)
        file_path = PROCESSED_VIDEOS_DIR / decoded_filename
        
        if not file_path.exists():
            # Try with original filename if decoded doesn't exist
            file_path = PROCESSED_VIDEOS_DIR / filename
        
        if not (file_path.exists() and file_path.is_file()):
            raise HTTPException(status_code=404, detail=f"Video file not found: {filename}")
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Handle range requests for video streaming
        range_header = request.headers.get('Range')
        
        if range_header:
            # Parse range header (format: "bytes=start-end")
            try:
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if range_match[1] else file_size - 1
                end = min(end, file_size - 1)
                
                # Calculate chunk size
                chunk_size = end - start + 1
                
                def iter_file_range():
                    with open(file_path, 'rb') as f:
                        f.seek(start)
                        remaining = chunk_size
                        while remaining > 0:
                            chunk = f.read(min(8192, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk
                
                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(chunk_size),
                    "Content-Type": "video/mp4",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range, Content-Range"
                }
                
                return StreamingResponse(
                    iter_file_range(),
                    status_code=206,
                    headers=headers,
                    media_type="video/mp4"
                )
            except (ValueError, IndexError):
                # Invalid range header, serve full file
                pass
        
        # Serve full file (no range request or invalid range)
        return FileResponse(
            str(file_path),
            media_type="video/mp4",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Accept-Ranges": "bytes",
                "Content-Type": "video/mp4",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "Range, Content-Range",
                "Content-Length": str(file_size)
            }
        )
            
    except Exception as e:
        logger.error(f"Error serving video {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Urban Mobility Data Living Laboratory (UMDL2) - YOLOv8 Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": video_processor.model is not None}

# Serve original videos with basic range support
@app.get("/videos/{filename:path}")
@app.head("/videos/{filename:path}")
@app.options("/videos/{filename:path}")
async def serve_original_video(filename: str, request: Request):
    try:
        decoded_filename = urllib.parse.unquote(filename)
        file_path = ORIGINAL_VIDEOS_DIR / decoded_filename
        if not file_path.exists():
            file_path = ORIGINAL_VIDEOS_DIR / filename
        if not (file_path.exists() and file_path.is_file()):
            raise HTTPException(status_code=404, detail=f"Original video not found: {filename}")

        file_size = file_path.stat().st_size
        range_header = request.headers.get('Range')
        if range_header:
            try:
                range_match = range_header.replace('bytes=', '').split('-')
                start = int(range_match[0]) if range_match[0] else 0
                end = int(range_match[1]) if range_match[1] else file_size - 1
                end = min(end, file_size - 1)
                chunk_size = end - start + 1

                def iter_file_range():
                    with open(file_path, 'rb') as f:
                        f.seek(start)
                        remaining = chunk_size
                        while remaining > 0:
                            chunk = f.read(min(8192, remaining))
                            if not chunk:
                                break
                            remaining -= len(chunk)
                            yield chunk

                headers = {
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(chunk_size),
                    "Content-Type": "video/mp4",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "Range, Content-Range"
                }
                return StreamingResponse(iter_file_range(), status_code=206, headers=headers, media_type="video/mp4")
            except (ValueError, IndexError):
                pass

        return FileResponse(
            str(file_path),
            media_type="video/mp4",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Accept-Ranges": "bytes",
                "Content-Type": "video/mp4",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "Range, Content-Range",
                "Content-Length": str(file_size)
            }
        )
    except Exception as e:
        logger.error(f"Error serving original video {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-video")
async def process_video(
    background_tasks: BackgroundTasks,
    location_id: str,
    video_filename: str
):
    """Process a video file with YOLOv8 and save with bounding boxes"""
    try:
        input_path = str(ORIGINAL_VIDEOS_DIR / location_id / video_filename)
        output_filename = f"{location_id}_{video_filename.replace('.mp4', '_processed.mp4')}"
        output_path = PROCESSED_VIDEOS_DIR / output_filename
        
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail=f"Video not found: {input_path}")
        
        if output_path.exists():
            logger.info(f"Processed video already exists: {output_path}")
            return {
                "status": "already_processed",
                "output_path": f"/processed/{output_filename}",
                "message": "Video was already processed"
            }
        
        background_tasks.add_task(
            video_processor.process_video,
            input_path,
            str(output_path)
        )
        
        return {
            "status": "processing",
            "output_path": f"/processed/{output_filename}",
            "message": "Video processing started in background"
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-all-videos")
async def process_all_videos(background_tasks: BackgroundTasks):
    """Process all three intersection videos"""
    locations = [
        {"id": "74th-Amsterdam-Columbus", "filename": "2025-02-13_06-00-04.mp4"},
        {"id": "Amsterdam-80th", "filename": "2025-02-13_06-00-04.mp4"},
        {"id": "Columbus-86th", "filename": "2025-02-13_06-00-06.mp4"}
    ]
    
    results = []
    for loc in locations:
        input_path = str(ORIGINAL_VIDEOS_DIR / loc['id'] / loc['filename'])
        output_filename = f"{loc['id']}_{loc['filename'].replace('.mp4', '_processed.mp4')}"
        output_path = PROCESSED_VIDEOS_DIR / output_filename
        
        if not os.path.exists(input_path):
            results.append({
                "location": loc['id'],
                "status": "error",
                "message": f"Video not found: {input_path}"
            })
            continue
        
        if output_path.exists():
            results.append({
                "location": loc['id'],
                "status": "already_processed",
                "output_path": f"/processed/{output_filename}"
            })
        else:
            background_tasks.add_task(
                video_processor.process_video,
                input_path,
                str(output_path)
            )
            results.append({
                "location": loc['id'],
                "status": "processing",
                "output_path": f"/processed/{output_filename}"
            })
    
    return {"results": results}

@app.get("/locations")
async def get_locations():
    """List known locations and original video availability (stub)."""
    items = []
    for loc in LOCATIONS:
        loc_id = loc["id"]
        filename = loc["filename"]
        # Original video under ORIGINAL_VIDEOS_DIR/<id>/<filename>
        vid_path = ORIGINAL_VIDEOS_DIR / loc_id / filename
        has_original = vid_path.exists()
        # Processed files follow pattern <id>_*_processed.mp4 in PROCESSED_VIDEOS_DIR
        processed = list(PROCESSED_VIDEOS_DIR.glob(f"{loc_id}_*_processed.mp4"))
        items.append({
            "id": loc_id,
            "name": loc["name"],
            "original_video": filename,
            "original_video_url": f"/videos/{loc_id}/{filename}" if has_original else None,
            "has_processed": len(processed) > 0,
            "processed_files": [p.name for p in processed],
        })
    return {"locations": items}

@app.get("/processing-status/{location_id}")
async def get_processing_status(location_id: str):
    """Check if a video has been processed"""
    processed_files = list(PROCESSED_VIDEOS_DIR.glob(f"{location_id}_*_processed.mp4"))
    
    if processed_files:
        return {
            "status": "completed",
            "files": [f"/processed/{f.name}" for f in processed_files]
        }
    else:
        return {"status": "not_processed"}

@app.get("/list-processed-videos")
async def list_processed_videos():
    """List all processed videos"""
    processed_files = list(PROCESSED_VIDEOS_DIR.glob("*_processed.mp4"))
    return {
        "videos": [
            {
                "filename": f.name,
                "path": f"/processed/{f.name}",
                "size_mb": f.stat().st_size / (1024 * 1024)
            }
            for f in processed_files
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
