#!/usr/bin/env python3
"""
Virtual Loop Configurations for Each Intersection Location
Defines detection zones for traffic counting
"""

from typing import Dict, List, Tuple
import json
import os
from pathlib import Path

# Virtual loop configurations for each location
# Each loop is defined by polygon points and counting direction

LOOP_CONFIGURATIONS: Dict[str, List[Dict]] = {
    
    # Richmond Hill Rd & Edinboro Rd, Staten Island
    "74th-Amsterdam-Columbus": [
        {
            "name": "Side_Street_Traffic",
            "zone_points": [
                (600, 200),   # Top-left
                (700, 200),   # Top-right
                (720, 350),   # Bottom-right
                (620, 350)    # Bottom-left
            ],
            "direction": "both",
            "description": "Side street traffic counting zone"
        }
    ],
    
    # Arthur Kill Rd & Storer Ave, Staten Island  
    "Amsterdam-80th": [
        {
            "name": "Arthur_Kill_Northbound",
            "zone_points": [
                (300, 600),   # Top-left
                (600, 580),   # Top-right
                (620, 650),   # Bottom-right
                (320, 670)    # Bottom-left
            ],
            "direction": "both",
            "description": "Arthur Kill Road northbound traffic"
        },
        {
            "name": "Arthur_Kill_Southbound", 
            "zone_points": [
                (700, 400),   # Top-left
                (1000, 380),  # Top-right
                (1020, 450),  # Bottom-right
                (720, 470)    # Bottom-left
            ],
            "direction": "both",
            "description": "Arthur Kill Road southbound traffic"
        },
        {
            "name": "Storer_Ave_Eastbound",
            "zone_points": [
                (500, 300),   # Top-left
                (800, 290),   # Top-right
                (820, 360),   # Bottom-right
                (520, 370)    # Bottom-left
            ],
            "direction": "both", 
            "description": "Storer Avenue eastbound traffic"
        }
    ],
    
    # Katonah Ave & East 241st St, Bronx
    "Columbus-86th": [
        {
            "name": "Katonah_Ave_Entry",
            "zone_points": [
                (150, 500),   # Top-left
                (450, 480),   # Top-right
                (470, 550),   # Bottom-right
                (170, 570)    # Bottom-left
            ],
            "direction": "entry",
            "description": "Katonah Avenue vehicles entering intersection"
        },
        {
            "name": "Katonah_Ave_Exit",
            "zone_points": [
                (900, 400),   # Top-left
                (1300, 380),  # Top-right  
                (1320, 450),  # Bottom-right
                (920, 470)    # Bottom-left
            ],
            "direction": "exit",
            "description": "Katonah Avenue vehicles exiting intersection"
        },
        {
            "name": "East_241st_Entry",
            "zone_points": [
                (600, 150),   # Top-left
                (700, 150),   # Top-right
                (720, 300),   # Bottom-right
                (620, 300)    # Bottom-left
            ],
            "direction": "entry",
            "description": "East 241st Street vehicles entering intersection"
        },
        {
            "name": "East_241st_Exit",
            "zone_points": [
                (550, 700),   # Top-left
                (650, 700),   # Top-right
                (670, 850),   # Bottom-right
                (570, 850)    # Bottom-left
            ],
            "direction": "exit", 
            "description": "East 241st Street vehicles exiting intersection"
        }
    ]
}

def get_loop_config(location_id: str) -> List[Dict]:
    """
    Get virtual loop configuration for a specific location
    
    Args:
        location_id: Location identifier (e.g., "74th-Amsterdam-Columbus")
        
    Returns:
        List of loop configuration dictionaries
    """
    base = LOOP_CONFIGURATIONS.get(location_id, [])
    # Load optional overrides from JSON file placed next to this module
    try:
        overrides_path = Path(__file__).with_name('loop_overrides.json')
        if overrides_path.exists():
            with open(overrides_path, 'r') as f:
                overrides = json.load(f)
            # Expected format: { "<locationId>": [ { name, zone_points, direction, description? }, ... ] }
            loc_overrides = overrides.get(location_id)
            if isinstance(loc_overrides, list) and len(loc_overrides) > 0:
                # If an override provides a loop with the same name, replace it; otherwise append
                by_name = {cfg["name"]: cfg for cfg in base if isinstance(cfg, dict) and "name" in cfg}
                for loop in loc_overrides:
                    if not isinstance(loop, dict) or "name" not in loop:
                        continue
                    by_name[loop["name"]] = loop
                return list(by_name.values())
    except Exception:
        # Silently ignore malformed overrides; fall back to base
        pass
    return base

def get_all_locations() -> List[str]:
    """Get list of all configured location IDs"""
    return list(LOOP_CONFIGURATIONS.keys())

def validate_loop_config(config: Dict) -> bool:
    """
    Validate a loop configuration dictionary
    
    Args:
        config: Loop configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["name", "zone_points", "direction"]
    
    # Check required keys
    for key in required_keys:
        if key not in config:
            return False
    
    # Validate zone points
    zone_points = config["zone_points"]
    if not isinstance(zone_points, list) or len(zone_points) < 3:
        return False
        
    # Check each point is a tuple/list of 2 numbers
    for point in zone_points:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return False
        if not all(isinstance(coord, (int, float)) for coord in point):
            return False
    
    # Validate direction
    valid_directions = ["entry", "exit", "both"]
    if config["direction"] not in valid_directions:
        return False
        
    return True

# Test configurations on import
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Validate all configurations
    for location_id, loops in LOOP_CONFIGURATIONS.items():
        logger.info(f"Validating {location_id}: {len(loops)} loops")
        
        for loop_config in loops:
            if validate_loop_config(loop_config):
                logger.info(f"  ✅ {loop_config['name']}: {loop_config['direction']} - "
                           f"{len(loop_config['zone_points'])} points")
            else:
                logger.error(f"  ❌ {loop_config['name']}: Invalid configuration")
                
    logger.info(f"Total locations: {len(LOOP_CONFIGURATIONS)}")
    logger.info(f"Total loops: {sum(len(loops) for loops in LOOP_CONFIGURATIONS.values())}")
