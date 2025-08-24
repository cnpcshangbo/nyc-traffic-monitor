#!/usr/bin/env python3
"""
Real-time traffic logging system for continuous JSON updates
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import threading
import logging

logger = logging.getLogger(__name__)

class RealTimeTrafficLogger:
    """
    Logs traffic data in real-time to JSON file for frontend consumption
    """
    
    def __init__(self, output_file: str = "processed_videos/live_traffic_data.json"):
        self.output_file = output_file
        self.traffic_data = {
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "total_vehicles": 0,
            "vehicle_types": {},
            "time_intervals": [],
            "recent_detections": [],
            "traffic_rate": {
                "vehicles_per_minute": 0.0,
                "current_interval": 0,
                "peak_interval": 0
            },
            "status": "active"
        }
        self.lock = threading.Lock()
        self.start_timestamp = time.time()
        self.current_interval_start = time.time()
        self.interval_duration = 15  # 15-second intervals
        self.current_interval_count = 0
        
        # Initialize the JSON file
        self._save_data()
        
    def log_vehicle_detection(self, vehicle_id: int, vehicle_class: str, 
                            confidence: float, timestamp: float, frame_number: int):
        """Log a new vehicle detection"""
        with self.lock:
            # Update totals
            self.traffic_data["total_vehicles"] += 1
            self.traffic_data["last_update"] = datetime.now().isoformat()
            
            # Update vehicle types
            if vehicle_class not in self.traffic_data["vehicle_types"]:
                self.traffic_data["vehicle_types"][vehicle_class] = 0
            self.traffic_data["vehicle_types"][vehicle_class] += 1
            
            # Add to recent detections (keep last 10)
            detection = {
                "vehicle_id": vehicle_id,
                "class": vehicle_class,
                "confidence": round(confidence, 3),
                "timestamp": timestamp,
                "frame_number": frame_number,
                "time_string": datetime.now().strftime("%H:%M:%S")
            }
            self.traffic_data["recent_detections"].append(detection)
            if len(self.traffic_data["recent_detections"]) > 10:
                self.traffic_data["recent_detections"].pop(0)
            
            # Update current interval
            self.current_interval_count += 1
            
            # Check if we need to create a new time interval
            current_time = time.time()
            if current_time - self.current_interval_start >= self.interval_duration:
                self._finalize_current_interval()
                self._start_new_interval()
            
            # Update traffic rate
            elapsed_minutes = (current_time - self.start_timestamp) / 60.0
            if elapsed_minutes > 0:
                self.traffic_data["traffic_rate"]["vehicles_per_minute"] = round(
                    self.traffic_data["total_vehicles"] / elapsed_minutes, 2
                )
            
            # Save to file
            self._save_data()
    
    def _finalize_current_interval(self):
        """Finalize the current time interval"""
        interval_data = {
            "start_time": self.current_interval_start,
            "end_time": time.time(),
            "duration_seconds": self.interval_duration,
            "vehicle_count": self.current_interval_count,
            "start_time_string": datetime.fromtimestamp(self.current_interval_start).strftime("%H:%M:%S"),
            "cumulative_total": self.traffic_data["total_vehicles"]
        }
        
        self.traffic_data["time_intervals"].append(interval_data)
        
        # Update peak interval
        if self.current_interval_count > self.traffic_data["traffic_rate"]["peak_interval"]:
            self.traffic_data["traffic_rate"]["peak_interval"] = self.current_interval_count
        
        # Keep only last 50 intervals for frontend performance
        if len(self.traffic_data["time_intervals"]) > 50:
            self.traffic_data["time_intervals"].pop(0)
    
    def _start_new_interval(self):
        """Start a new time interval"""
        self.current_interval_start = time.time()
        self.current_interval_count = 0
        self.traffic_data["traffic_rate"]["current_interval"] = 0
    
    def _save_data(self):
        """Save traffic data to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            
            # Write to temporary file first, then move to avoid corruption
            temp_file = self.output_file + ".tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.traffic_data, f, indent=2)
            
            # Atomic move
            os.rename(temp_file, self.output_file)
            
        except Exception as e:
            logger.error(f"Failed to save traffic data: {e}")
    
    def finalize(self):
        """Finalize logging (call when processing is complete)"""
        with self.lock:
            if self.current_interval_count > 0:
                self._finalize_current_interval()
            
            self.traffic_data["status"] = "completed"
            self.traffic_data["last_update"] = datetime.now().isoformat()
            
            # Final summary
            total_time_minutes = (time.time() - self.start_timestamp) / 60.0
            self.traffic_data["summary"] = {
                "total_processing_time_minutes": round(total_time_minutes, 2),
                "average_vehicles_per_minute": round(
                    self.traffic_data["total_vehicles"] / max(total_time_minutes, 0.1), 2
                ),
                "total_intervals": len(self.traffic_data["time_intervals"]),
                "peak_interval_count": self.traffic_data["traffic_rate"]["peak_interval"]
            }
            
            self._save_data()
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current traffic statistics"""
        with self.lock:
            return {
                "total_vehicles": self.traffic_data["total_vehicles"],
                "vehicle_types": dict(self.traffic_data["vehicle_types"]),
                "vehicles_per_minute": self.traffic_data["traffic_rate"]["vehicles_per_minute"],
                "intervals_count": len(self.traffic_data["time_intervals"]),
                "status": self.traffic_data["status"]
            }