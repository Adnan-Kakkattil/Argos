# PrismTrack Complete Workflow Documentation

## Complete End-to-End Workflow

### 1. Platform Admin Creates Tenant

**User**: Platform Admin  
**Action**: Login → Create Tenant  
**Result**: 
- Tenant created with unique `tenant_org_id` (5-8 characters)
- Tenant admin credentials generated
- Tenant appears in dashboard

### 2. Client Admin (Tenant Admin) Login

**User**: Tenant Admin  
**Action**: Login with tenant credentials  
**Result**: 
- Access to tenant dashboard
- Can see tenant, companies, branches, and users
- Can download agents for different org_ids

### 3. Client Admin Downloads Agent MSI

**User**: Tenant Admin  
**Action**: Click "Download Agent" button for an org_id  
**Backend Process**:
1. Validates org_id belongs to tenant
2. Serves MSI file from `backend/static/agents/PrismTrackAgent.msi`
3. Returns file with filename: `PrismTrack_Agent_{org_id}.msi`

**Frontend Process**:
1. Calls `GET /api/v1/tenant/download-agent/{org_id}`
2. Receives MSI file as binary
3. Triggers browser download
4. Shows success message

**Result**: MSI file downloaded to user's machine

### 4. User Runs MSI Installer

**User**: Employee/IT Admin  
**Action**: Double-click `PrismTrack_Agent_{org_id}.msi`  
**MSI Installation Process**:

1. **Extract Files**:
   - Extracts to: `C:\Program Files\PrismTrack\Agent\`
   - Files extracted:
     - `PrismTrackAgent.exe` (Python executable)
     - `config.json` (configuration template)
     - `installer_script.ps1` (PowerShell installation script)

2. **Run Custom Action**:
   - Executes `installer_script.ps1`
   - Script performs:
     - Collects system information:
       - Hardware UUID (from Windows registry)
       - Machine name
       - Username (whoami)
       - Hostname
       - UPN email (tries AD, falls back to local)
     - Updates `config.json` with org_id (from config.json template)
     - Registers agent with backend:
       - `POST /api/v1/agent/register`
       - Sends: `org_id`, `org_type`, `machine_name`, `hardware_uuid`
       - Receives: `agent_token`
     - Saves `agent_token` to `config.json`
     - Starts `PrismTrackAgent.exe`

3. **Show Completion**:
   - Displays "Installation Complete" message
   - Agent is now running

### 5. PrismTrackAgent.exe Runs

**Process**: Background process (or Windows Service)  
**Functionality**:

1. **Load Configuration**:
   - Reads `config.json` from installation directory
   - Gets `org_id`, `api_base`, `agent_token`

2. **Main Loop** (runs continuously):
   - **Every 30 seconds**:
     - Collects active window title
     - Collects process name
     - Checks idle status (5+ minutes no input = idle)
     - Sends telemetry data:
       - `POST /api/v1/agent/telemetry`
       - Header: `X-Agent-Token: {agent_token}`
       - Body: `{telemetry: [{window_title, process_name, timestamp, is_idle}]}`
   - **Every 30 seconds**:
     - Sends heartbeat:
       - `POST /api/v1/agent/heartbeat`
       - Header: `X-Agent-Token: {agent_token}`
       - Body: `{agent_token, status: "ONLINE"}`

3. **Data Collection**:
   - Window title: Active window title
   - Process name: Process name of active window
   - Idle detection: No user input for 5+ minutes
   - Timestamp: UTC timestamp for each record

### 6. Backend Receives Data

**Backend Process**:
1. Receives telemetry data
2. Validates agent token
3. Stores data in `telemetry` table
4. Updates agent `last_seen` timestamp
5. Updates agent status to `ONLINE`

### 7. Client Admin Views Data

**User**: Tenant Admin  
**Action**: View dashboard/agents  
**Backend**: 
- `GET /api/v1/tenant/agents` - List all agents
- `GET /api/v1/tenant/agents/{agent_id}/telemetry` - View telemetry data

**Frontend**: Displays agent status and productivity data

---

## File Locations

### Backend Static Files
- `backend/static/agents/PrismTrackAgent.msi` - MSI installer template
- `backend/static/agents/PrismTrackAgent.exe` - Agent executable (for reference)

### Agent Installation
- `C:\Program Files\PrismTrack\Agent\PrismTrackAgent.exe` - Agent executable
- `C:\Program Files\PrismTrack\Agent\config.json` - Agent configuration
- `C:\Program Files\PrismTrack\Agent\installer_script.ps1` - Installation script

### MSI Builder
- `installer/wix/main.wxs` - WiX source file
- `installer/installer_script.ps1` - PowerShell installation script
- `installer/Cargo.toml` - Rust project configuration
- `installer/src/main.rs` - Dummy Rust binary (for cargo-wix)

### Agent Source
- `PrismTrackAgent/` - Python agent source code
- `PrismTrackAgent/dist/PrismTrackAgent.exe` - Built executable

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/platform-admin/login` - Platform admin login
- `POST /api/v1/auth/tenant/login` - Tenant admin login
- `POST /api/v1/auth/refresh` - Refresh token

### Platform Admin
- `GET /api/v1/platform-admin/tenants` - List tenants
- `POST /api/v1/platform-admin/tenants` - Create tenant
- `GET /api/v1/platform-admin/tenants/{id}/stats` - Client 360 stats

### Tenant Admin
- `GET /api/v1/tenant/companies` - List companies
- `POST /api/v1/tenant/companies` - Create company
- `GET /api/v1/tenant/org-ids` - List all org_ids
- `GET /api/v1/tenant/download-agent/{org_id}` - Download MSI installer

### Agent
- `POST /api/v1/agent/register` - Register agent
- `POST /api/v1/agent/heartbeat` - Send heartbeat
- `POST /api/v1/agent/telemetry` - Submit telemetry data

---

## Configuration

### Backend (.env)
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=prismtrack
SECRET_KEY=your-secret-key
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

### Agent (config.json)
```json
{
  "org_id": "S18NZD4",
  "api_base": "http://localhost:8000/api/v1",
  "agent_token": "generated_token_here",
  "heartbeat_interval": 30,
  "telemetry_interval": 30,
  "idle_threshold_seconds": 300
}
```

---

## Build Process

### 1. Build Agent Executable
```bash
cd PrismTrackAgent
pip install -r requirements.txt
python build_exe.py
# Output: dist/PrismTrackAgent.exe
```

### 2. Build MSI Installer
```bash
cd installer
cargo wix
# Output: PrismTrackAgent.msi
```

### 3. Copy Files to Static Directory
```bash
# Copy MSI and EXE to backend static directory
cp installer/PrismTrackAgent.msi backend/static/agents/
cp PrismTrackAgent/dist/PrismTrackAgent.exe backend/static/agents/
```

### 4. Start Backend
```bash
python -m backend.main
```

### 5. Start Frontend
```bash
cd frontend
python -m http.server 8080
```

---

## Testing the Complete Workflow

1. **Platform Admin**:
   - Login: `admin` / `admin123`
   - Create a tenant
   - Note the tenant credentials

2. **Tenant Admin**:
   - Login with tenant credentials
   - View dashboard
   - Click "Download Agent" for tenant org_id
   - Verify MSI downloads

3. **Install MSI**:
   - Run the downloaded MSI on a Windows machine
   - Verify installation completes
   - Check `C:\Program Files\PrismTrack\Agent\` for files
   - Verify `config.json` has correct org_id and agent_token

4. **Verify Agent**:
   - Check agent appears in backend database
   - Verify agent sends heartbeat
   - Verify agent sends telemetry data
   - View data in tenant admin dashboard

---

## Troubleshooting

### MSI Download Fails
- Check backend is running
- Verify MSI exists in `backend/static/agents/`
- Check CORS configuration
- Verify authentication token

### Agent Installation Fails
- Check PowerShell execution policy
- Verify admin privileges
- Check network connectivity to backend
- Review installer script logs

### Agent Not Registering
- Verify org_id is correct in config.json
- Check backend API is accessible
- Verify org_id exists in database
- Check backend logs for errors

### Agent Not Sending Data
- Verify agent_token is set in config.json
- Check agent is running (Task Manager)
- Verify network connectivity
- Check backend logs for telemetry submissions

---

## Security Notes

- Agent token is stored in config.json (plain text)
- For production, consider encrypting the token
- Use HTTPS for API communication in production
- Restrict CORS origins to specific domains
- Use strong JWT secrets
- Change default admin password

---

## Next Steps

1. **Production Deployment**:
   - Use HTTPS for API
   - Encrypt agent tokens
   - Set up proper logging
   - Configure production database

2. **Enhancements**:
   - Windows Service installation
   - Automatic updates
   - Screenshot capture
   - Advanced analytics
   - Real-time dashboard

3. **Testing**:
   - End-to-end testing
   - Load testing
   - Security testing
   - User acceptance testing

