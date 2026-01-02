"""
API Client for PrismTrack Agent
"""
import requests
import sys
from typing import List, Dict, Optional
from datetime import datetime, timezone

class ApiClient:
    """Handles all API communication with PrismTrack backend"""
    
    def __init__(self, api_base: str, agent_token: str):
        self.api_base = api_base
        self.agent_token = agent_token
        self.headers = {
            'X-Agent-Token': agent_token,
            'Content-Type': 'application/json'
        }
    
    def heartbeat(self) -> bool:
        """
        Send heartbeat to backend
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.api_base}/agent/heartbeat"
        
        payload = {
            "agent_token": self.agent_token,
            "status": "ONLINE"
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
            return False
    
    def submit_telemetry(self, telemetry_data: List[Dict]) -> bool:
        """
        Submit telemetry data to backend
        
        Args:
            telemetry_data: List of telemetry records, each containing:
                - window_title: str
                - process_name: str
                - timestamp: str (ISO format)
                - is_idle: bool
                - screenshot_url: Optional[str]
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.api_base}/agent/telemetry"
        
        payload = {
            "telemetry": telemetry_data,
            "agent_token": self.agent_token  # Include in body for compatibility
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            records_count = data.get('records_count', len(telemetry_data))
            print(f"Telemetry submitted: {records_count} records")
            return True
            
        except Exception as e:
            print(f"Error submitting telemetry: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('detail', 'Unknown error')
                    print(f"  Error detail: {error_detail}")
                except:
                    pass
            return False

