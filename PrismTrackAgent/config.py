"""
Configuration Management for PrismTrack Agent
"""
import json
import os
import sys
from pathlib import Path
from typing import Optional

class Config:
    """Manages agent configuration"""
    
    def __init__(self, org_id: str, api_base: str, agent_token: Optional[str] = None,
                 heartbeat_interval: int = 30, telemetry_interval: int = 30,
                 idle_threshold_seconds: int = 300):
        self.org_id = org_id
        self.api_base = api_base
        self.agent_token = agent_token
        self.heartbeat_interval = heartbeat_interval
        self.telemetry_interval = telemetry_interval
        self.idle_threshold_seconds = idle_threshold_seconds
    
    @staticmethod
    def get_config_path() -> Path:
        """Get path to config.json file"""
        # Try to get from same directory as executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = Path(sys.executable).parent
        else:
            # Running as script
            base_path = Path(__file__).parent
        
        return base_path / "config.json"
    
    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from config.json"""
        import sys
        
        config_path = cls.get_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return cls(
                    org_id=data.get('org_id', ''),
                    api_base=data.get('api_base', 'http://localhost:8000/api/v1'),
                    agent_token=data.get('agent_token'),
                    heartbeat_interval=data.get('heartbeat_interval', 30),
                    telemetry_interval=data.get('telemetry_interval', 30),
                    idle_threshold_seconds=data.get('idle_threshold_seconds', 300)
                )
            except Exception as e:
                print(f"Error loading config: {e}")
                # Return default config
                return cls(org_id='', api_base='http://localhost:8000/api/v1')
        else:
            # Create default config file
            default_config = cls(org_id='', api_base='http://localhost:8000/api/v1')
            default_config.save()
            return default_config
    
    def save(self):
        """Save configuration to config.json"""
        config_path = self.get_config_path()
        
        data = {
            'org_id': self.org_id,
            'api_base': self.api_base,
            'agent_token': self.agent_token,
            'heartbeat_interval': self.heartbeat_interval,
            'telemetry_interval': self.telemetry_interval,
            'idle_threshold_seconds': self.idle_threshold_seconds
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

