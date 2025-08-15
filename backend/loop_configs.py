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
            "name": "Main_Road_Entry",
            "zone_points": [
                (200, 400),   # Top-left
                (500, 380),   # Top-right  
                (520, 450),   # Bottom-right
                (220, 470)    # Bottom-left
            ],
            "direction": "entry",
            "description": "Main road vehicles entering intersection"
        },
        {
            "name": "Main_Road_Exit", 
            "zone_points": [
                (800, 500),   # Top-left
                (1200, 480),  # Top-right
                (1220, 550),  # Bottom-right
                (820, 570)    # Bottom-left
            ],
            "direction": "exit",
            "description": "Main road vehicles exiting intersection"
        },
        {
            "name": "Side_Street_Entry",
            "zone_points": [
                (600, 200),   # Top-left
                (700, 200),   # Top-right
                (720, 350),   # Bottom-right
                (620, 350)    # Bottom-left
            ],
            "direction": "entry",
            "description": "Side street vehicles entering intersection"
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