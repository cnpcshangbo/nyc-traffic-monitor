#!/usr/bin/env python3
"""
Virtual Loop Configurations for Each Intersection Location
Defines detection zones for traffic counting
"""

from typing import Dict, List, Tuple

# Virtual loop configurations for each location
# Each loop is defined by polygon points and counting direction

LOOP_CONFIGURATIONS: Dict[str, List[Dict]] = {
    
    # Richmond Hill Rd & Edinboro Rd, Staten Island
    "74th-Amsterdam-Columbus": [
        {
            "name": "Side_Street_Traffic",
            "zone_points": [
                (630, 220),   # Top-left - narrower and more centered
                (670, 220),   # Top-right - only 40px wide
                (670, 260),   # Bottom-right - shorter 40px height
                (630, 260)    # Bottom-left - focused detection zone
            ],
            "direction": "entry",
            "description": "Side street traffic counting zone"
        }
    ],
    
    # Arthur Kill Rd & Storer Ave, Staten Island  
    "Amsterdam-80th": [
        {
            "name": "Main_Traffic_Flow",
            "zone_points": [
                (407, 400),   # Top-left - bottom center for 854x480 video
                (447, 400),   # Top-right - only 40px wide
                (447, 440),   # Bottom-right - 40px height
                (407, 440)    # Bottom-left - centered horizontally
            ],
            "direction": "entry",
            "description": "Main traffic flow counting zone"
        }
    ],
    
    # Katonah Ave & East 241st St, Bronx
    "Columbus-86th": [
        {
            "name": "Primary_Traffic_Lane",
            "zone_points": [
                (400, 500),   # Top-left - moved to active traffic area
                (440, 500),   # Top-right - only 40px wide
                (440, 540),   # Bottom-right - 40px height
                (400, 540)    # Bottom-left - positioned for vehicle detection
            ],
            "direction": "entry",
            "description": "Primary traffic lane counting zone"
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
    return LOOP_CONFIGURATIONS.get(location_id, [])

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