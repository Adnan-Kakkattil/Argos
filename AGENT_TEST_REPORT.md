# PrismTrack Agent Test Report

## Test Configuration
- **Org ID**: S18NZD4
- **API Base**: http://localhost:8000/api/v1
- **Agent Executable**: PrismTrackAgent.exe (or main.py)

## Test Steps

### 1. Configuration Setup
- Updated `PrismTrackAgent/config.json` with:
  - `org_id`: "S18NZD4"
  - `api_base`: "http://localhost:8000/api/v1"
  - `agent_token`: null (to force fresh registration)

### 2. Agent Execution
- Started agent using: `python main.py` or `PrismTrackAgent.exe`
- Agent should:
  1. Load configuration
  2. Collect system information (hardware UUID, machine name, etc.)
  3. Register with backend if no agent_token exists
  4. Start heartbeat loop (every 30 seconds)
  5. Start telemetry collection loop (every 30 seconds)

### 3. Verification Steps

#### Check Agent Registration
```python
from backend.core.database import SessionLocal
from backend.models.agent import Agent

db = SessionLocal()
agents = db.query(Agent).filter(Agent.org_id == 'S18NZD4').all()
```

Expected:
- Agent record created in database
- `agent_token` generated and saved to config.json
- `status` set to "ONLINE"
- `last_seen` updated regularly

#### Check Heartbeat
- Agent sends heartbeat every 30 seconds
- Backend updates `last_seen` timestamp
- Status remains "ONLINE"

#### Check Telemetry Data
```python
from backend.models.telemetry import Telemetry

telemetry = db.query(Telemetry).filter(
    Telemetry.agent_id == agent_id
).order_by(Telemetry.timestamp.desc()).limit(10).all()
```

Expected:
- Telemetry records created every 30 seconds
- Records contain:
  - `window_title`: Active window title
  - `process_name`: Process name
  - `is_idle`: Boolean (true if idle > 5 minutes)
  - `timestamp`: UTC timestamp

## Expected Behavior

1. **Registration**:
   - Agent collects system info
   - Sends POST to `/api/v1/agent/register`
   - Receives `agent_token`
   - Saves token to config.json

2. **Heartbeat**:
   - Every 30 seconds: POST to `/api/v1/agent/heartbeat`
   - Updates agent status to ONLINE
   - Updates `last_seen` timestamp

3. **Telemetry**:
   - Every 30 seconds: Collects active window info
   - POST to `/api/v1/agent/telemetry`
   - Sends array of telemetry records

## Troubleshooting

### Agent Not Registering
- Check backend is running on http://localhost:8000
- Verify org_id "S18NZD4" exists in database
- Check network connectivity
- Review agent console output for errors

### No Telemetry Data
- Verify agent is running (check process)
- Check agent_token is set in config.json
- Verify agent is sending telemetry (check backend logs)
- Check database for telemetry records

### Agent Stops Running
- Check for Python errors in console
- Verify all dependencies installed
- Check Windows Event Viewer for errors
- Review agent logs if available

## Test Results

Run the test and document:
- [ ] Agent registered successfully
- [ ] Agent token saved to config.json
- [ ] Heartbeat working (last_seen updating)
- [ ] Telemetry data being collected
- [ ] Telemetry data visible in database
- [ ] Agent visible in tenant admin dashboard

