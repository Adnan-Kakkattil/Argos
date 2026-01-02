# PrismTrack Agent

Python-based productivity tracking agent for PrismTrack Employee Tracking System.

## Overview

PrismTrack Agent runs on employee machines to track basic productivity metrics:
- Active window title
- Process name
- Idle detection (no user input for 5+ minutes)
- Sends data to PrismTrack backend API

## Features

- **System Information Collection**: Automatically collects hardware UUID, machine name, username, hostname, and UPN email
- **Agent Registration**: Registers with PrismTrack backend on first run
- **Productivity Tracking**: Tracks active window and process every 30 seconds
- **Idle Detection**: Detects when user is idle (no input for 5+ minutes)
- **Heartbeat**: Sends heartbeat to backend every 30 seconds
- **Telemetry Submission**: Sends productivity data to backend every 30 seconds

## Requirements

- Windows 10/11 (64-bit)
- Python 3.8+ (for development)
- Administrator privileges (for installation as service)

## Installation

### Development Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create `config.json`:
```json
{
  "org_id": "YOUR_ORG_ID_HERE",
  "api_base": "http://localhost:8000/api/v1",
  "agent_token": null,
  "heartbeat_interval": 30,
  "telemetry_interval": 30,
  "idle_threshold_seconds": 300
}
```

3. Run the agent:
```bash
python main.py
```

### Build Executable

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build executable:
```bash
python build_exe.py
```

3. The executable will be created in `dist/PrismTrackAgent.exe`

## Configuration

The agent uses `config.json` for configuration:

- **org_id**: Organization ID (tenant, company, or branch)
- **api_base**: Base URL of PrismTrack API
- **agent_token**: Token received after registration (auto-populated)
- **heartbeat_interval**: Seconds between heartbeats (default: 30)
- **telemetry_interval**: Seconds between telemetry submissions (default: 30)
- **idle_threshold_seconds**: Seconds of no input to consider idle (default: 300)

## Workflow

1. **First Run**:
   - Agent loads `config.json`
   - Collects system information
   - Registers with backend API
   - Receives `agent_token`
   - Saves token to `config.json`

2. **Subsequent Runs**:
   - Agent loads `config.json` (including `agent_token`)
   - Starts tracking loop immediately

3. **Tracking Loop** (every 5 seconds):
   - Checks if heartbeat is due (every 30 seconds)
   - Checks if telemetry is due (every 30 seconds)
   - Collects active window and process
   - Checks idle status
   - Sends data to backend

## API Endpoints Used

- `POST /api/v1/agent/register` - Register agent
- `POST /api/v1/agent/heartbeat` - Send heartbeat
- `POST /api/v1/agent/telemetry` - Submit telemetry data

## Files

- `main.py` - Main application entry point
- `config.py` - Configuration management
- `system_info.py` - System information collection
- `registration.py` - Agent registration
- `tracking.py` - Productivity tracking
- `api_client.py` - API communication
- `idle_detection.py` - Idle detection utilities
- `build_exe.py` - Build script for executable

## Troubleshooting

### Agent won't register
- Check network connection
- Verify API endpoint is correct in `config.json`
- Ensure `org_id` is valid
- Check backend logs for errors

### No telemetry data
- Verify agent_token is set in `config.json`
- Check network connection
- Verify API endpoint is accessible
- Check backend logs

### Idle detection not working
- Ensure `pywin32` is installed correctly
- Check Windows permissions
- Verify `win32api` is available

## Security Notes

- Agent token is stored in `config.json` (plain text)
- For production, consider encrypting the token
- Agent should run with minimal privileges
- Network communication should use HTTPS in production

## License

Part of PrismTrack Employee Tracking System

