"""
Build script to create PrismTrackAgent.exe using PyInstaller
"""
import PyInstaller.__main__
import os
import sys
from pathlib import Path

def build_exe():
    """Build executable using PyInstaller"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # PyInstaller arguments
    args = [
        'main.py',                          # Main script
        '--onefile',                        # Create single executable
        '--name=PrismTrackAgent',           # Output name
        '--add-data=config.json;.',         # Include config.json
        '--hidden-import=win32timezone',    # Hidden imports
        '--hidden-import=win32api',
        '--hidden-import=win32gui',
        '--hidden-import=win32process',
        '--hidden-import=win32con',
        '--hidden-import=win32event',
        '--collect-all=win32timezone',      # Collect all from module
        '--noconsole',                      # No console window (for service)
        # '--windowed',                     # Alternative to --noconsole
    ]
    
    # If config.json doesn't exist, create a template
    config_path = script_dir / 'config.json'
    if not config_path.exists():
        import json
        template_config = {
            "org_id": "YOUR_ORG_ID_HERE",
            "api_base": "http://localhost:8000/api/v1",
            "agent_token": None,
            "heartbeat_interval": 30,
            "telemetry_interval": 30,
            "idle_threshold_seconds": 300
        }
        with open(config_path, 'w') as f:
            json.dump(template_config, f, indent=2)
        print("Created template config.json")
    
    print("Building PrismTrackAgent.exe...")
    print(f"Working directory: {script_dir}")
    print()
    
    # Change to script directory
    os.chdir(script_dir)
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print()
    print("=" * 60)
    print("Build complete!")
    print(f"Executable location: {script_dir / 'dist' / 'PrismTrackAgent.exe'}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        build_exe()
    except Exception as e:
        print(f"Error building executable: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

