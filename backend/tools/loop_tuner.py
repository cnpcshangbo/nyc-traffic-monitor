#!/usr/bin/env python3
"""
Interactive Loop Tuner Tool

Best-practice workflow to tune virtual loop positions for a location:
- Preview a specific frame (by timestamp) of the input video
- Interactively draw/edit loop polygons on the frame
- Save overrides to backend/loop_overrides.json (non-invasive to code)
- Process a short preview segment (e.g., 20–60s) using the overrides
- Review the generated preview MP4; iterate until satisfied

Usage examples:
  python backend/tools/loop_tuner.py \
    --location Amsterdam-80th \
    --input backend/videos/Amsterdam-80th_2025-02-13_06-00-04.mp4 \
    --timestamp 5 \
    --duration 30

Keys (in the OpenCV window):
  - Left click: add point to current polygon
  - 'n': start a new polygon
  - 'u': undo last point in current polygon
  - 'x': delete current polygon (if empty, deletes last polygon)
  - 'c' or Enter: close current polygon
  - 's': save overrides to loop_overrides.json and continue
  - 'q' or ESC: quit without saving

Note: This tool writes to backend/loop_overrides.json which is merged
      with base configurations in backend/loop_configs.py
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

import cv2

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT
OVERRIDES_PATH = BACKEND_DIR / 'loop_overrides.json'


def grab_frame(video_path: str, timestamp: float) -> Tuple[bool, any, int, int, int]:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return False, None, 0, 0, 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_idx = int(timestamp * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    if not ok:
        print(f"❌ Failed to read frame at {timestamp}s (idx {frame_idx})")
        return False, None, 0, 0, int(fps)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap.release()
    return True, frame, w, h, int(fps)


class PolygonEditor:
    def __init__(self, frame):
        self.frame = frame.copy()
        self.display = frame.copy()
        self.polygons: List[List[Tuple[int, int]]] = []
        self.current: List[Tuple[int, int]] = []
        self.window = 'Loop Tuner'
        self.help_overlay()

    def help_overlay(self):
        overlay = self.display
        help_lines = [
            "Click to add points · n: new polygon · u: undo · x: delete · c/Enter: close · s: save · q: quit",
        ]
        y = 30
        for line in help_lines:
            cv2.putText(overlay, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 24

    def draw(self):
        self.display = self.frame.copy()
        # draw existing polygons
        for poly in self.polygons:
            if len(poly) >= 2:
                for i in range(len(poly)):
                    cv2.circle(self.display, poly[i], 4, (0, 255, 255), -1)
                    cv2.line(self.display, poly[i], poly[(i + 1) % len(poly)], (0, 255, 255), 2)
        # draw current polygon
        for p in self.current:
            cv2.circle(self.display, p, 4, (0, 200, 0), -1)
        if len(self.current) >= 2:
            for i in range(len(self.current) - 1):
                cv2.line(self.display, self.current[i], self.current[i + 1], (0, 200, 0), 2)
        self.help_overlay()
        cv2.imshow(self.window, self.display)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current.append((x, y))
            self.draw()

    def close_current(self):
        if len(self.current) >= 3:
            self.polygons.append(self.current.copy())
            self.current.clear()
            self.draw()

    def undo(self):
        if self.current:
            self.current.pop()
        else:
            if self.polygons:
                self.polygons.pop()
        self.draw()

    def delete_current(self):
        if self.current:
            self.current.clear()
        elif self.polygons:
            self.polygons.pop()
        self.draw()


def load_overrides() -> Dict[str, List[Dict]]:
    if OVERRIDES_PATH.exists():
        with open(OVERRIDES_PATH, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def save_overrides(overrides: Dict[str, List[Dict]]):
    with open(OVERRIDES_PATH, 'w') as f:
        json.dump(overrides, f, indent=2)
    print(f"💾 Saved overrides to {OVERRIDES_PATH}")


def run_preview(location_id: str, input_video: str, out_dir: str, duration: float):
    # Lazy import to avoid heavy deps until needed
    sys.path.append(str(BACKEND_DIR))
    from video_processor_with_loops import VideoProcessorWithLoops

    MODEL_PATH = os.getenv(
        'MODEL_PATH',
        '/home/roboticslab/City College Dropbox/BO SHANG/gsv_truck/2025/ws/runs/best.pt'
    )

    os.makedirs(out_dir, exist_ok=True)
    stem = Path(input_video).stem
    preview_mp4 = Path(out_dir) / f"{stem}_preview_with_loops.mp4"
    preview_json = Path(out_dir) / f"{stem}_preview_traffic_data.json"

    print(f"▶️  Generating preview for {duration}s ...")
    processor = VideoProcessorWithLoops(MODEL_PATH, location_id)
    ok = processor.process_video_with_loops(
        input_video,
        str(preview_mp4),
        str(preview_json),
        conf_threshold=0.6,
        max_duration_seconds=duration,
    )
    if ok:
        print(f"✅ Preview ready:\n  Video: {preview_mp4}\n  Data:  {preview_json}")
        print("Open the video file to review loop placement. If adjustments are needed, rerun this tool.")
    else:
        print("❌ Preview generation failed. Check logs for details.")


def main():
    parser = argparse.ArgumentParser(description='Interactive virtual loop tuner')
    parser.add_argument('--location', '-l', required=True, help='Location ID (e.g., Amsterdam-80th)')
    parser.add_argument('--input', '-i', required=True, help='Path to input MP4')
    parser.add_argument('--timestamp', '-t', type=float, default=5.0, help='Timestamp (s) to preview frame')
    parser.add_argument('--duration', '-d', type=float, default=30.0, help='Preview duration (s) to process')
    parser.add_argument('--output-dir', '-o', default=str(BACKEND_DIR / 'processed_videos'), help='Output directory')
    parser.add_argument('--loop-name', default='Custom_Loop_1', help='Default name for the first polygon')
    parser.add_argument('--direction', default='both', choices=['entry', 'exit', 'both'], help='Counting direction')
    args = parser.parse_args()

    ok, frame, w, h, fps = grab_frame(args.input, args.timestamp)
    if not ok:
        sys.exit(1)

    editor = PolygonEditor(frame)
    cv2.namedWindow(editor.window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(editor.window, editor.on_mouse)
    editor.draw()

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == ord('q') or key == 27:  # ESC
            print('Exiting without saving.')
            cv2.destroyAllWindows()
            sys.exit(0)
        elif key == ord('n'):
            # start a new polygon if current is closed
            if len(editor.current) >= 3:
                editor.close_current()
            editor.current = []
            editor.draw()
        elif key == ord('u'):
            editor.undo()
        elif key == ord('x'):
            editor.delete_current()
        elif key == ord('c') or key == 13:  # Enter
            editor.close_current()
        elif key == ord('s'):
            # Save overrides
            if editor.current and len(editor.current) >= 3:
                editor.close_current()
            if not editor.polygons:
                print('⚠️ No polygons to save. Draw at least one loop.')
                continue
            overrides = load_overrides()
            loops: List[Dict] = []
            # Name polygons sequentially if multiple were drawn
            for idx, poly in enumerate(editor.polygons, start=1):
                name = args.loop_name if idx == 1 else f"{args.loop_name}_{idx}"
                loops.append({
                    'name': name,
                    'zone_points': poly,
                    'direction': args.direction,
                    'description': f'Tuned via loop_tuner at t={args.timestamp}s'
                })
            overrides[args.location] = loops
            save_overrides(overrides)
            cv2.destroyAllWindows()
            break

    # Generate a short preview
    run_preview(args.location, args.input, args.output_dir, args.duration)


if __name__ == '__main__':
    main()

