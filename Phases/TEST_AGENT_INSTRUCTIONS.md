# How to Test PrismTrack Agent with Org ID S18NZD4

## Quick Start

### Option 1: Run with Python (Recommended for Testing)
```bash
cd PrismTrackAgent
python main.py
```

### Option 2: Run with Executable
```bash
cd PrismTrackAgent
.\dist\PrismTrackAgent.exe
```

## What to Expect

1. **Agent Startup**:
   - Prints banner: "PrismTrack Agent"
   - Loads configuration from `config.json`
   - Shows: Org ID, API Base
   - Collects system information

2. **Registration** (if no agent_token):
   - "Agent not registered. Registering with backend..."
   - Sends registration request
   - Receives agent_token
   - Saves token to config.json
   - "Agent registered successfully!"

3. **Running**:
   - "Starting productivity tracking..."
   - Sends heartbeat every 30 seconds
   - Collects telemetry every 30 seconds
   - Shows activity in console

## Verify Agent is Working

### Check Agent Status
```bash
python test_agent_s18nzd4.py
```

Expected output:
- Agent found with org_id S18NZD4
- Status: ONLINE
- Last Seen: Recent (within last 2 minutes)
- Telemetry Records: Increasing

### Check Database Directly
```python
from backend.core.database import SessionLocal
from backend.models.agent import Agent

db = SessionLocal()
agent = db.query(Agent).filter(Agent.org_id == 'S18NZD4').first()
print(f"Status: {agent.status}")
print(f"Last Seen: {agent.last_seen}")
```

### Check Telemetry Data
```python
from backend.models.telemetry import Telemetry

telemetry = db.query(Telemetry).filter(
    Telemetry.agent_id == agent.id
).order_by(Telemetry.timestamp.desc()).limit(10).all()

for t in telemetry:
    print(f"{t.timestamp}: {t.window_title} (Idle: {t.is_idle})")
```

## Current Status

✅ **Agent Registered**: Agent ID 17
✅ **Configuration**: org_id = S18NZD4
✅ **Telemetry Working**: 4 records collected earlier
⚠️ **Agent Not Running**: Last seen 5.5 hours ago

## To Continue Testing

1. **Start the agent** (see Quick Start above)
2. **Wait 30-60 seconds** for first heartbeat and telemetry
3. **Run test script** to verify:
   ```bash
   python test_agent_s18nzd4.py
   ```
4. **Check dashboard** in frontend to see agent data

## Troubleshooting

### Agent Not Registering
- Check backend is running: `http://localhost:8000`
- Verify org_id "S18NZD4" exists in database
- Check network connectivity
- Review console output for errors

### No Telemetry Data
- Verify agent is running (check process list)
- Check agent_token is set in config.json
- Wait at least 30 seconds for first telemetry
- Check backend logs for errors

### Agent Stops
- Check for Python errors in console
- Verify all dependencies installed
- Check Windows Event Viewer
- Review agent logs

## Configuration File

Location: `PrismTrackAgent/config.json`

```json
{
  "org_id": "S18NZD4",
  "api_base": "http://localhost:8000/api/v1",
  "agent_token": "7cdJWFA2GXSlOvFTjTwODyKEAMDKhOTfBqph3rEJwkQ",
  "heartbeat_interval": 30,
  "telemetry_interval": 30,
  "idle_threshold_seconds": 300
}
```

## Test Results Summary

✅ Registration: SUCCESS
✅ Telemetry Collection: SUCCESS  
✅ Data Storage: SUCCESS
⚠️ Currently Running: NO (needs restart)

The agent is working correctly! Just restart it to continue tracking.

