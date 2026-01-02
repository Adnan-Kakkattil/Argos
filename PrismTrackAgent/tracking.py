"""
Productivity Tracking for PrismTrack Agent
"""
import win32gui
import win32process
import psutil
import sys
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
from api_client import ApiClient
from system_info import SystemInfo

class ProductivityTracker:
    """Tracks employee productivity metrics"""
    
    def __init__(self, api_client: ApiClient, system_info: SystemInfo, idle_threshold_seconds: int = 300):
        self.api_client = api_client
        self.system_info = system_info
        self.idle_threshold_seconds = idle_threshold_seconds
        self.last_input_time = datetime.now(timezone.utc)
    
    def collect_and_send(self):
        """Collect telemetry data and send to API"""
        try:
            # Get active window information
            window_title, process_name = self.get_active_window()
            
            # Check idle status
            is_idle = self.is_idle()
            
            # Create telemetry record
            telemetry_data = [{
                "window_title": window_title,
                "process_name": process_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_idle": is_idle
            }]
            
            # Send to API
            self.api_client.submit_telemetry(telemetry_data)
            
        except Exception as e:
            print(f"Error in collect_and_send: {e}")
    
    def get_active_window(self) -> Tuple[str, str]:
        """
        Get active window title and process name
        
        Returns:
            Tuple[str, str]: (window_title, process_name)
        """
        try:
            # Get foreground window handle
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                window_title = "Unknown"
            
            # Get process ID from window
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
            
            return window_title, process_name
            
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown", "Unknown"
    
    def is_idle(self) -> bool:
        """
        Check if user is idle (no input for threshold seconds)
        
        Returns:
            bool: True if user is idle, False otherwise
        """
        try:
            import win32api
            
            # Get last input time
            last_input = win32api.GetLastInputInfo()
            current_time = win32api.GetTickCount()
            
            # Calculate idle time in seconds
            idle_time_seconds = (current_time - last_input) / 1000.0
            
            # Check if idle threshold exceeded
            is_idle = idle_time_seconds > self.idle_threshold_seconds
            
            if is_idle:
                print(f"User is idle (no input for {idle_time_seconds:.0f} seconds)")
            
            return is_idle
            
        except ImportError:
            # win32api not available, assume not idle
            print("Warning: win32api not available, cannot detect idle state")
            return False
        except Exception as e:
            print(f"Error checking idle status: {e}")
            return False

