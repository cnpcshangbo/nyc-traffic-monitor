#!/usr/bin/env python3
"""
Virtual Inductive Loop System for Traffic Volume Counting
Implements vehicle tracking and counting across virtual detection zones
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import logging
from real_time_logger import RealTimeTrafficLogger

logger = logging.getLogger(__name__)

@dataclass
class VehicleDetection:
    """Single vehicle detection data"""
    id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    centroid: Tuple[int, int]
    timestamp: float
    frame_number: int

@dataclass
class LoopCrossing:
    """Vehicle crossing a virtual loop"""
    vehicle_id: int
    loop_name: str
    class_name: str
    confidence: float
    timestamp: float
    frame_number: int
    direction: str  # 'entry' or 'exit'
    centroid: Tuple[int, int]

@dataclass
class TrafficCount:
    """Traffic count data for a time interval"""
    start_time: float
    end_time: float
    interval_seconds: int
    total_count: int
    vehicle_counts: Dict[str, int]
    crossings: List[LoopCrossing]

class VehicleTracker:
    """Simple centroid-based vehicle tracker"""
    
    def __init__(self, max_disappeared: int = 30, max_distance: float = 100):
        self.next_object_id = 0
        self.objects = {}  # object_id -> centroid
        self.disappeared = {}  # object_id -> frames_disappeared
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
    def register(self, centroid: Tuple[int, int]) -> int:
        """Register a new object and return its ID"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        object_id = self.next_object_id
        self.next_object_id += 1
        return object_id
        
    def deregister(self, object_id: int):
        """Remove an object from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]
        
    def update(self, detections: List[Tuple[int, int]]) -> Dict[int, Tuple[int, int]]:
        """Update tracker with new detections and return object_id -> centroid mapping"""
        
        if len(detections) == 0:
            # No detections, mark all existing objects as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects.copy()
            
        # If no existing objects, register all detections as new objects
        if len(self.objects) == 0:
            for detection in detections:
                self.register(detection)
        else:
            # Compute distance matrix between existing objects and detections
            object_ids = list(self.objects.keys())
            object_centroids = [self.objects[obj_id] for obj_id in object_ids]
            
            # Calculate distances
            distances = np.zeros((len(object_centroids), len(detections)))
            for i, obj_centroid in enumerate(object_centroids):
                for j, det_centroid in enumerate(detections):
                    distances[i, j] = np.linalg.norm(np.array(obj_centroid) - np.array(det_centroid))
            
            # Find optimal assignment using simple greedy approach
            used_detection_indices = set()
            used_object_indices = set()
            
            # Sort by distance and assign
            row_indices, col_indices = np.unravel_index(np.argsort(distances, axis=None), distances.shape)
            
            for row, col in zip(row_indices, col_indices):
                if row in used_object_indices or col in used_detection_indices:
                    continue
                    
                if distances[row, col] <= self.max_distance:
                    # Update existing object
                    object_id = object_ids[row]
                    self.objects[object_id] = detections[col]
                    self.disappeared[object_id] = 0
                    
                    used_object_indices.add(row)
                    used_detection_indices.add(col)
            
            # Handle unassigned detections (register as new objects)
            for j in range(len(detections)):
                if j not in used_detection_indices:
                    self.register(detections[j])
                    
            # Handle unassigned existing objects (mark as disappeared)
            for i in range(len(object_ids)):
                if i not in used_object_indices:
                    object_id = object_ids[i]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
        
        return self.objects.copy()

class VirtualInductiveLoop:
    """Virtual inductive loop for traffic counting"""
    
    def __init__(self, name: str, zone_points: List[Tuple[int, int]], direction: str = "both"):
        """
        Initialize virtual loop
        
        Args:
            name: Loop name (e.g., "Main_Lane_Entry")
            zone_points: List of (x,y) points defining the loop zone polygon
            direction: Counting direction - "entry", "exit", or "both"
        """
        self.name = name
        self.zone_points = np.array(zone_points, dtype=np.int32)
        self.direction = direction
        self.crossings: List[LoopCrossing] = []
        self.previous_positions: Dict[int, Tuple[int, int]] = {}  # vehicle_id -> previous centroid
        self.counted_vehicles: Dict[int, float] = {}  # vehicle_id -> timestamp when counted
        self.recent_crossings: List[Tuple[Tuple[int, int], float]] = []  # (centroid, timestamp) for spatial duplicate detection
        self.cooldown_seconds = 0.5  # Minimum time between counts for same area
        
    def is_point_in_zone(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside the loop zone using cv2.pointPolygonTest"""
        # Ensure point is in correct format for OpenCV
        point_float = (float(point[0]), float(point[1]))
        result = cv2.pointPolygonTest(self.zone_points, point_float, False)
        return result >= 0
        
    def check_crossing(self, vehicle_id: int, current_centroid: Tuple[int, int], 
                      vehicle_data: VehicleDetection) -> Optional[LoopCrossing]:
        """
        Check if vehicle crossed the loop zone with duplicate prevention
        
        Returns LoopCrossing if a crossing occurred, None otherwise
        """
        current_in_zone = self.is_point_in_zone(current_centroid)
        current_timestamp = vehicle_data.timestamp
        
        # Clean up old recent crossings (older than cooldown period)
        self.recent_crossings = [
            (centroid, timestamp) for centroid, timestamp in self.recent_crossings
            if current_timestamp - timestamp < self.cooldown_seconds
        ]
        
        # Clean up old counted vehicles (older than cooldown period)
        self.counted_vehicles = {
            vid: timestamp for vid, timestamp in self.counted_vehicles.items()
            if current_timestamp - timestamp < self.cooldown_seconds
        }
        
        if vehicle_id in self.previous_positions:
            previous_centroid = self.previous_positions[vehicle_id]
            previous_in_zone = self.is_point_in_zone(previous_centroid)
            
            # Detect crossing: was outside, now inside (entry) or was inside, now outside (exit)
            crossing_type = None
            if not previous_in_zone and current_in_zone:
                crossing_type = "entry"
            elif previous_in_zone and not current_in_zone:
                crossing_type = "exit"
                
            # Check if we should count this crossing based on direction setting
            if crossing_type and (self.direction == "both" or self.direction == crossing_type):
                
                # Duplicate prevention checks
                
                # 1. Check if this vehicle was already counted recently
                if vehicle_id in self.counted_vehicles:
                    logger.debug(f"Loop {self.name}: Vehicle {vehicle_id} already counted recently, skipping")
                    self.previous_positions[vehicle_id] = current_centroid
                    return None
                
                # 2. Check if a vehicle was counted in this spatial area recently (handles ID reassignment)
                min_distance_threshold = 50  # pixels
                for recent_centroid, recent_timestamp in self.recent_crossings:
                    distance = np.linalg.norm(np.array(current_centroid) - np.array(recent_centroid))
                    if distance < min_distance_threshold:
                        logger.debug(f"Loop {self.name}: Vehicle detected too close to recent crossing "
                                   f"(distance: {distance:.1f}px), skipping")
                        self.previous_positions[vehicle_id] = current_centroid
                        return None
                
                # Valid crossing - record it
                crossing = LoopCrossing(
                    vehicle_id=vehicle_id,
                    loop_name=self.name,
                    class_name=vehicle_data.class_name,
                    confidence=vehicle_data.confidence,
                    timestamp=vehicle_data.timestamp,
                    frame_number=vehicle_data.frame_number,
                    direction=crossing_type,
                    centroid=current_centroid
                )
                
                # Record this crossing to prevent duplicates
                self.crossings.append(crossing)
                self.counted_vehicles[vehicle_id] = current_timestamp
                self.recent_crossings.append((current_centroid, current_timestamp))
                
                logger.info(f"Loop {self.name}: Vehicle {vehicle_id} ({vehicle_data.class_name}) "
                           f"crossed {crossing_type} at frame {vehicle_data.frame_number} - COUNT: {len(self.crossings)}")
                return crossing
        
        # Update position for next frame
        self.previous_positions[vehicle_id] = current_centroid
        return None
        
    def get_total_count(self) -> int:
        """Get total number of vehicles that crossed this loop"""
        return len(self.crossings)
        
    def get_counts_by_class(self) -> Dict[str, int]:
        """Get vehicle counts grouped by class"""
        counts = {}
        for crossing in self.crossings:
            class_name = crossing.class_name
            counts[class_name] = counts.get(class_name, 0) + 1
        return counts
        
    def draw_zone(self, frame: np.ndarray, color: Tuple[int, int, int] = (0, 255, 255), 
                  thickness: int = 3) -> np.ndarray:
        """Draw the loop zone on the frame with enhanced visibility and traffic counter"""
        
        # Draw semi-transparent filled polygon for better visibility
        overlay = frame.copy()
        cv2.fillPoly(overlay, [self.zone_points], color)
        frame = cv2.addWeighted(frame, 0.85, overlay, 0.15, 0)
        
        # Draw bold outline
        cv2.polylines(frame, [self.zone_points], isClosed=True, color=color, thickness=thickness)
        
        # Add label with traffic counter for better readability
        if len(self.zone_points) > 0:
            label_pos = tuple(self.zone_points[0])
            
            # Get current traffic count
            total_count = self.get_total_count()
            vehicle_counts = self.get_counts_by_class()
            
            # Create simplified label with live traffic count
            label_text = f"{self.name.replace('_', ' ')}"
            count_text = f"Traffic Count: {total_count}"
            
            # Add vehicle breakdown if available
            if vehicle_counts:
                count_details = []
                for vehicle_type, count in vehicle_counts.items():
                    count_details.append(f"{vehicle_type}: {count}")
                detail_text = " | ".join(count_details)
            else:
                detail_text = "No vehicles detected"
            
            # Configure fonts
            font = cv2.FONT_HERSHEY_SIMPLEX
            title_font_scale = 0.8
            count_font_scale = 0.9
            detail_font_scale = 0.6
            font_thickness = 2
            
            # Get text dimensions
            (title_width, title_height), _ = cv2.getTextSize(label_text, font, title_font_scale, font_thickness)
            (count_width, count_height), _ = cv2.getTextSize(count_text, font, count_font_scale, font_thickness)
            (detail_width, detail_height), _ = cv2.getTextSize(detail_text, font, detail_font_scale, font_thickness-1)
            
            # Calculate total label dimensions
            max_width = max(title_width, count_width, detail_width)
            total_height = title_height + count_height + detail_height + 30  # padding
            
            # Position the label box
            bg_x1 = max(0, label_pos[0] - 10)
            bg_y1 = max(0, label_pos[1] - total_height - 10)
            bg_x2 = min(frame.shape[1], label_pos[0] + max_width + 20)
            bg_y2 = min(frame.shape[0], label_pos[1] + 10)
            
            # Draw semi-transparent background for better readability
            label_overlay = frame.copy()
            cv2.rectangle(label_overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
            frame = cv2.addWeighted(frame, 0.7, label_overlay, 0.3, 0)
            
            # Draw colored border
            cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 3)
            
            # Draw text lines
            text_y = label_pos[1] - 15
            
            # Title
            cv2.putText(frame, label_text, (label_pos[0], text_y), 
                       font, title_font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)
            text_y -= title_height + 8
            
            # Traffic count (prominent)
            cv2.putText(frame, count_text, (label_pos[0], text_y), 
                       font, count_font_scale, color, font_thickness, cv2.LINE_AA)
            text_y -= count_height + 8
            
            # Vehicle details
            cv2.putText(frame, detail_text, (label_pos[0], text_y), 
                       font, detail_font_scale, (200, 200, 200), font_thickness-1, cv2.LINE_AA)
            
        return frame

class VirtualLoopSystem:
    """Complete virtual inductive loop system for traffic monitoring"""
    
    def __init__(self, location_id: str, enable_real_time_logging: bool = True):
        self.location_id = location_id
        self.loops: Dict[str, VirtualInductiveLoop] = {}
        self.all_crossings: List[LoopCrossing] = []
        self.start_time = time.time()
        self.video_fps = 30  # Default, should be set when processing video
        
        # Real-time logging
        self.real_time_logger = None
        if enable_real_time_logging:
            log_file = f"processed_videos/live_traffic_{location_id}.json"
            self.real_time_logger = RealTimeTrafficLogger(log_file)
        
    def add_loop(self, loop: VirtualInductiveLoop):
        """Add a virtual loop to the system"""
        self.loops[loop.name] = loop
        logger.info(f"Added virtual loop: {loop.name} with {len(loop.zone_points)} points")
        
    def process_detections(self, detections: List[VehicleDetection], frame_number: int) -> List[LoopCrossing]:
        """
        Process vehicle detections with YOLO tracking IDs and update loop crossings
        
        Args:
            detections: List of vehicle detections for current frame (with YOLO tracking IDs)
            frame_number: Current frame number
            
        Returns:
            List of new crossings detected in this frame
        """
        # Check all loops for crossings using YOLO tracking IDs directly
        new_crossings = []
        for detection in detections:
            # Use YOLO tracking ID directly (much more reliable than centroid tracking)
            vehicle_id = detection.id
            
            for loop in self.loops.values():
                crossing = loop.check_crossing(vehicle_id, detection.centroid, detection)
                if crossing:
                    new_crossings.append(crossing)
                    self.all_crossings.append(crossing)
                    
                    # Log to real-time system
                    if self.real_time_logger:
                        self.real_time_logger.log_vehicle_detection(
                            vehicle_id=crossing.vehicle_id,
                            vehicle_class=crossing.class_name,
                            confidence=crossing.confidence,
                            timestamp=crossing.timestamp,
                            frame_number=crossing.frame_number
                        )
        
        return new_crossings
        
    def get_traffic_counts(self, interval_seconds: int = 15) -> List[TrafficCount]:
        """
        Get traffic counts aggregated by time intervals
        
        Args:
            interval_seconds: Time interval for aggregation (default: 15 seconds)
            
        Returns:
            List of TrafficCount objects for each time interval
        """
        if not self.all_crossings:
            return []
            
        # Sort crossings by timestamp
        sorted_crossings = sorted(self.all_crossings, key=lambda x: x.timestamp)
        
        # Determine time range
        start_time = sorted_crossings[0].timestamp
        end_time = sorted_crossings[-1].timestamp
        
        # Create time intervals
        intervals = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = current_start + interval_seconds
            
            # Get crossings in this interval
            interval_crossings = [
                crossing for crossing in sorted_crossings
                if current_start <= crossing.timestamp < current_end
            ]
            
            # Count by vehicle class
            vehicle_counts = {}
            for crossing in interval_crossings:
                class_name = crossing.class_name
                vehicle_counts[class_name] = vehicle_counts.get(class_name, 0) + 1
            
            traffic_count = TrafficCount(
                start_time=current_start,
                end_time=current_end,
                interval_seconds=interval_seconds,
                total_count=len(interval_crossings),
                vehicle_counts=vehicle_counts,
                crossings=interval_crossings
            )
            intervals.append(traffic_count)
            
            current_start = current_end
        
        return intervals
        
    def export_to_json(self, output_path: str, interval_seconds: int = 15) -> bool:
        """
        Export traffic data to JSON file
        
        Args:
            output_path: Path to save JSON file
            interval_seconds: Time interval for aggregation
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get aggregated traffic counts
            traffic_counts = self.get_traffic_counts(interval_seconds)
            
            # Build export data structure
            export_data = {
                "location_id": self.location_id,
                "processing_timestamp": datetime.now().isoformat(),
                "video_fps": self.video_fps,
                "total_crossings": len(self.all_crossings),
                "interval_seconds": interval_seconds,
                "virtual_loops": {},
                "time_series": []
            }
            
            # Add loop-specific data
            for loop_name, loop in self.loops.items():
                export_data["virtual_loops"][loop_name] = {
                    "total_count": loop.get_total_count(),
                    "vehicle_counts": loop.get_counts_by_class(),
                    "zone_points": loop.zone_points.tolist(),
                    "direction": loop.direction
                }
            
            # Add time series data
            for traffic_count in traffic_counts:
                time_entry = {
                    "timestamp": traffic_count.start_time,
                    "interval_seconds": traffic_count.interval_seconds,
                    "total_count": traffic_count.total_count,
                    "vehicle_counts": traffic_count.vehicle_counts,
                    "crossings": [
                        {
                            "vehicle_id": crossing.vehicle_id,
                            "loop_name": crossing.loop_name,
                            "class_name": crossing.class_name,
                            "confidence": round(crossing.confidence, 3),
                            "direction": crossing.direction,
                            "centroid": crossing.centroid
                        }
                        for crossing in traffic_count.crossings
                    ]
                }
                export_data["time_series"].append(time_entry)
            
            # Write JSON file with custom encoder for numpy types
            def convert_numpy_types(obj):
                """Convert numpy types to native Python types"""
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            # Convert all numpy types in the data
            def clean_for_json(obj):
                if isinstance(obj, dict):
                    return {k: clean_for_json(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [clean_for_json(v) for v in obj]
                elif isinstance(obj, tuple):
                    return tuple(clean_for_json(v) for v in obj)
                else:
                    return convert_numpy_types(obj)
            
            clean_data = clean_for_json(export_data)
            
            with open(output_path, 'w') as f:
                json.dump(clean_data, f, indent=2)
                
            logger.info(f"Exported traffic data to {output_path}")
            logger.info(f"Total crossings: {len(self.all_crossings)}")
            logger.info(f"Time intervals: {len(traffic_counts)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to export traffic data: {e}")
            return False
        
    def draw_loops(self, frame: np.ndarray) -> np.ndarray:
        """Draw all virtual loops on the frame with distinct colors"""
        
        # Define colors for different loop types/directions
        loop_colors = {
            'entry': (0, 255, 0),    # Green for entry loops
            'exit': (0, 0, 255),     # Red for exit loops  
            'both': (255, 0, 255),   # Magenta for bidirectional loops
        }
        
        # Assign colors based on loop names for consistency
        loop_name_colors = {
            'Side_Street_Traffic': (255, 255, 0),     # Cyan (blue-ish) for the main traffic loop
            'Arthur_Kill_Northbound': (255, 0, 255),  # Magenta
            'Arthur_Kill_Southbound': (0, 255, 255),  # Yellow
            'Storer_Ave_Eastbound': (255, 165, 0),    # Orange
            'Katonah_Ave_Entry': (0, 255, 0),         # Green
            'Katonah_Ave_Exit': (0, 0, 255),          # Red
            'East_241st_Entry': (255, 255, 0),        # Cyan
            'East_241st_Exit': (255, 0, 128),         # Pink
        }
        
        for loop_name, loop in self.loops.items():
            # Use specific color for the loop name, fallback to direction color
            color = loop_name_colors.get(loop_name, loop_colors.get(loop.direction, (0, 255, 255)))
            frame = loop.draw_zone(frame, color)
            
        return frame
        
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total_crossings = len(self.all_crossings)
        
        # Count by vehicle class
        class_counts = {}
        for crossing in self.all_crossings:
            class_name = crossing.class_name
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
        # Count by loop
        loop_counts = {}
        for loop_name, loop in self.loops.items():
            loop_counts[loop_name] = loop.get_total_count()
        
        return {
            "location_id": self.location_id,
            "total_loops": len(self.loops),
            "total_crossings": total_crossings,
            "crossings_by_class": class_counts,
            "crossings_by_loop": loop_counts,
            "processing_duration": time.time() - self.start_time
        }
    
    def finalize_real_time_logging(self):
        """Finalize real-time logging when processing is complete"""
        if self.real_time_logger:
            self.real_time_logger.finalize()