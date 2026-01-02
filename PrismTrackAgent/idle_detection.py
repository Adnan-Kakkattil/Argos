"""
Idle Detection Utilities for PrismTrack Agent
"""
import sys
from typing import Optional

def get_idle_time() -> Optional[float]:
    """
    Get idle time in seconds (time since last user input)
    
    Returns:
        Optional[float]: Idle time in seconds, or None if unavailable
    """
    try:
        import win32api
        
        last_input = win32api.GetLastInputInfo()
        current_time = win32api.GetTickCount()
        
        # Calculate idle time in seconds
        idle_time_seconds = (current_time - last_input) / 1000.0
        
        return idle_time_seconds
        
    except ImportError:
        # win32api not available
        return None
    except Exception as e:
        print(f"Error getting idle time: {e}")
        return None

def is_idle(idle_threshold_seconds: int = 300) -> bool:
    """
    Check if user is idle
    
    Args:
        idle_threshold_seconds: Threshold in seconds (default: 300 = 5 minutes)
    
    Returns:
        bool: True if user is idle, False otherwise
    """
    idle_time = get_idle_time()
    
    if idle_time is None:
        return False
    
    return idle_time > idle_threshold_seconds

