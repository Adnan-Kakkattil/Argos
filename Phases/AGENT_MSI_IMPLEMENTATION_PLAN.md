# MSI Agent Installer & Rust Agent Implementation Plan

## Overview
Build a Windows MSI installer that downloads, installs, and registers a Rust-based productivity tracking agent. The agent will track basic employee productivity metrics and send data to the PrismTrack backend.

## Architecture

### Components
1. **MSI Installer** (WiX Toolset) - Windows installer
2. **Rust Agent** (PrismTrackAgent.exe) - Productivity tracking executable
3. **Backend API** - Already implemented, needs agent download endpoint

---

## Phase 1: Backend Agent Download Endpoint

### 1.1 Create Agent Download Endpoint
**File**: `backend/api/v1/endpoints/tenant.py`

**Endpoint**: `GET /api/v1/tenant/download-agent/{org_id}`

**Functionality**:
- Validate org_id exists and user has access
- Generate agent configuration with org_id embedded
- Create agent.zip containing:
  - `PrismTrackAgent.exe` (Rust binary)
  - `config.json` (contains org_id, API endpoint)
  - `installer.ps1` (optional PowerShell script for silent install)
- Return zip file as download

**Response**: Binary zip file with appropriate headers

---

## Phase 2: Rust Agent Development

### 2.1 Project Structure
```
agent/
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── config.rs
│   ├── system_info.rs
│   ├── registration.rs
│   ├── tracking.rs
│   ├── api_client.rs
│   └── idle_detection.rs
├── build.rs
└── README.md
```

### 2.2 Dependencies (Cargo.toml)
```toml
[package]
name = "prismtrack-agent"
version = "0.1.0"
edition = "2021"

[dependencies]
reqwest = { version = "0.11", features = ["json", "blocking"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
windows = { version = "0.52", features = ["Win32_System_SystemInformation", "Win32_UI_WindowsAndMessaging", "Win32_Foundation"] }
uuid = { version = "1.0", features = ["v4"] }
winapi = { version = "0.3", features = ["winuser", "processthreadsapi", "sysinfoapi"] }
```

### 2.3 Core Functionality

#### 2.3.1 System Information Collection (`system_info.rs`)
```rust
pub struct SystemInfo {
    pub hardware_uuid: String,      // Machine GUID from registry
    pub machine_name: String,        // Computer name
    pub username: String,            // Current user (whoami)
    pub hostname: String,            // Full hostname
    pub upn_email: Option<String>,   // User Principal Name (if available)
}

impl SystemInfo {
    pub fn collect() -> Result<SystemInfo, Error> {
        // Get hardware UUID from Windows registry
        // Get machine name
        // Get current username
        // Get hostname
        // Try to get UPN email from AD or local account
    }
}
```

**Windows Registry Path for Machine GUID**:
- `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\MachineGuid`

**Methods**:
- `get_hardware_uuid()` - Read from registry
- `get_machine_name()` - `GetComputerNameExW`
- `get_username()` - `GetUserNameW` or `whoami` command
- `get_hostname()` - `GetComputerNameExW` with `ComputerNameDnsFullyQualified`
- `get_upn_email()` - Try AD query or local account email

#### 2.3.2 Agent Registration (`registration.rs`)
```rust
pub async fn register_agent(
    api_base: &str,
    org_id: &str,
    system_info: &SystemInfo
) -> Result<String, Error> {
    // POST /api/v1/agent/register
    // Body: {
    //   "org_id": org_id,
    //   "machine_name": system_info.machine_name,
    //   "hardware_uuid": system_info.hardware_uuid
    // }
    // Returns: agent_token
}
```

#### 2.3.3 Productivity Tracking (`tracking.rs`)
```rust
pub struct ProductivityData {
    pub window_title: String,
    pub process_name: String,
    pub timestamp: DateTime<Utc>,
    pub is_idle: bool,
}

pub struct Tracker {
    agent_token: String,
    api_base: String,
}

impl Tracker {
    pub async fn start_tracking(&self) {
        // Main tracking loop
        // Every 30 seconds:
        //   1. Get active window title
        //   2. Get process name
        //   3. Check idle status
        //   4. Send telemetry batch
    }
    
    fn get_active_window(&self) -> Result<(String, String), Error> {
        // Use Windows API to get:
        // - Active window title
        // - Process name of active window
    }
    
    fn is_idle(&self) -> bool {
        // Check last input time
        // Consider idle if no input for 5+ minutes
    }
}
```

**Windows API Calls**:
- `GetForegroundWindow()` - Get active window
- `GetWindowTextW()` - Get window title
- `GetWindowThreadProcessId()` - Get process ID
- `GetLastInputInfo()` - Check idle status

#### 2.3.4 API Client (`api_client.rs`)
```rust
pub struct ApiClient {
    base_url: String,
    agent_token: String,
}

impl ApiClient {
    pub async fn heartbeat(&self) -> Result<(), Error> {
        // POST /api/v1/agent/heartbeat
        // Header: X-Agent-Token: {token}
    }
    
    pub async fn submit_telemetry(&self, data: Vec<TelemetryData>) -> Result<(), Error> {
        // POST /api/v1/agent/telemetry
        // Header: X-Agent-Token: {token}
        // Body: { "telemetry": [...] }
    }
}
```

#### 2.3.5 Main Application (`main.rs`)
```rust
#[tokio::main]
async fn main() {
    // 1. Load config.json (org_id, api_base)
    // 2. Collect system information
    // 3. Register agent with backend
    // 4. Save agent_token to local file
    // 5. Start tracking loop
    // 6. Send heartbeat every 30 seconds
    // 7. Collect and send telemetry every 30 seconds
}
```

### 2.4 Configuration File (`config.json`)
```json
{
  "org_id": "S18NZD4",
  "api_base": "http://localhost:8000/api/v1",
  "heartbeat_interval": 30,
  "telemetry_interval": 30,
  "idle_threshold_seconds": 300
}
```

---

## Phase 3: MSI Installer (WiX Toolset)

### 3.1 Project Structure
```
installer/
├── PrismTrackAgent.wxs          # WiX source file
├── Product.wxs                   # Main installer definition
├── CustomActions.wxs             # Custom actions (registration, etc.)
├── build.bat                     # Build script
├── agent.zip                     # Agent package (generated)
└── README.md
```

### 3.2 Installer Workflow

#### Step 1: Pre-Installation
- Check Windows version (Windows 10+)
- Check admin privileges
- Check if agent already installed

#### Step 2: Download Agent Package
**Custom Action**: Download agent.zip from backend
```
URL: {API_BASE}/api/v1/tenant/download-agent/{ORG_ID}
Method: GET
Headers: Authorization: Bearer {TENANT_TOKEN}
Save to: %TEMP%\PrismTrackAgent.zip
```

**PowerShell Script** (embedded in MSI):
```powershell
$orgId = $env:ORG_ID
$apiBase = $env:API_BASE
$token = $env:TENANT_TOKEN

$url = "$apiBase/api/v1/tenant/download-agent/$orgId"
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-WebRequest -Uri $url -Headers $headers -OutFile "$env:TEMP\PrismTrackAgent.zip"
```

#### Step 3: Extract Agent Package
- Extract `agent.zip` to `%ProgramFiles%\PrismTrack\Agent\`
- Extract files:
  - `PrismTrackAgent.exe`
  - `config.json`

#### Step 4: Collect System Information
**Custom Action**: Run PowerShell to collect system info
```powershell
# Get Hardware UUID
$machineGuid = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Cryptography" -Name "MachineGuid").MachineGuid

# Get Machine Name
$machineName = $env:COMPUTERNAME

# Get Username
$username = $env:USERNAME
$fullUsername = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Get Hostname
$hostname = [System.Net.Dns]::GetHostByName($env:COMPUTERNAME).HostName

# Get UPN Email (try AD first, then local)
$upnEmail = $null
try {
    $user = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $upnEmail = $user.Name
    # Try to get email from AD
    $adUser = Get-ADUser -Identity $user.Name -Properties UserPrincipalName -ErrorAction SilentlyContinue
    if ($adUser) {
        $upnEmail = $adUser.UserPrincipalName
    }
} catch {
    # Not in AD domain, use local account
    $upnEmail = "$username@$hostname"
}
```

#### Step 5: Register Agent
**Custom Action**: Call agent registration API
```powershell
$apiBase = "http://localhost:8000/api/v1"
$orgId = "S18NZD4"  # From config or MSI property

$body = @{
    org_id = $orgId
    machine_name = $machineName
    hardware_uuid = $machineGuid
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$apiBase/agent/register" -Method POST -Body $body -ContentType "application/json"

# Save agent_token
$agentToken = $response.agent_token
$tokenPath = "$env:ProgramFiles\PrismTrack\Agent\agent_token.txt"
$agentToken | Out-File -FilePath $tokenPath -Encoding ASCII
```

#### Step 6: Install as Windows Service
- Install `PrismTrackAgent.exe` as Windows Service
- Set to auto-start on boot
- Start service immediately

#### Step 7: Post-Installation
- Create desktop shortcut (optional)
- Show completion message
- Log installation details

### 3.3 WiX Source File Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="PrismTrack Agent" Language="1033" Version="1.0.0" 
           Manufacturer="PrismTrack" UpgradeCode="YOUR-GUID-HERE">
    
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />
    
    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    
    <MediaTemplate />
    
    <!-- Features -->
    <Feature Id="ProductFeature" Title="PrismTrack Agent" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
    
    <!-- Custom Actions -->
    <CustomAction Id="DownloadAgent" Script="ps1" Execute="deferred" Impersonate="no" />
    <CustomAction Id="ExtractAgent" Script="ps1" Execute="deferred" />
    <CustomAction Id="CollectSystemInfo" Script="ps1" Execute="immediate" />
    <CustomAction Id="RegisterAgent" Script="ps1" Execute="deferred" />
    <CustomAction Id="InstallService" Script="ps1" Execute="deferred" />
    
    <!-- Installation Sequence -->
    <InstallExecuteSequence>
      <Custom Action="CollectSystemInfo" After="CostFinalize" />
      <Custom Action="DownloadAgent" After="CollectSystemInfo" />
      <Custom Action="ExtractAgent" After="DownloadAgent" />
      <Custom Action="RegisterAgent" After="ExtractAgent" />
      <Custom Action="InstallService" After="RegisterAgent" />
    </InstallExecuteSequence>
  </Product>
  
  <!-- Components -->
  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="PrismTrack">
          <Directory Id="AGENTFOLDER" Name="Agent" />
        </Directory>
      </Directory>
    </Directory>
  </Fragment>
  
  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="AGENTFOLDER">
      <!-- Agent files will be added here -->
    </ComponentGroup>
  </Fragment>
</Wix>
```

---

## Phase 4: Build & Packaging

### 4.1 Build Rust Agent
```bash
cd agent
cargo build --release
# Output: target/release/PrismTrackAgent.exe
```

### 4.2 Create Agent Package
```bash
# Create agent.zip
mkdir -p agent-package
cp target/release/PrismTrackAgent.exe agent-package/
cp config.json agent-package/
cd agent-package
zip -r ../agent.zip .
```

### 4.3 Build MSI Installer
```bash
cd installer
# Use WiX Toolset
candle PrismTrackAgent.wxs
light PrismTrackAgent.wixobj -out PrismTrackAgent.msi
```

---

## Phase 5: Testing

### 5.1 Agent Registration Test
- Install MSI on test machine
- Verify agent registers with backend
- Check agent appears in dashboard

### 5.2 Productivity Tracking Test
- Verify telemetry data is collected
- Check window titles and process names
- Verify idle detection works
- Check heartbeat is sent regularly

### 5.3 Service Test
- Verify service starts on boot
- Test service restart
- Test service uninstall

---

## Implementation Checklist

### Backend
- [ ] Create agent download endpoint
- [ ] Generate agent.zip with embedded org_id
- [ ] Add authentication to download endpoint

### Rust Agent
- [ ] Set up Rust project structure
- [ ] Implement system info collection (hardware UUID, username, hostname, UPN)
- [ ] Implement agent registration
- [ ] Implement productivity tracking (window title, process name)
- [ ] Implement idle detection
- [ ] Implement API client (heartbeat, telemetry)
- [ ] Implement main application loop
- [ ] Build release binary
- [ ] Test on Windows

### MSI Installer
- [ ] Set up WiX project
- [ ] Create installer UI
- [ ] Implement download custom action
- [ ] Implement extract custom action
- [ ] Implement system info collection
- [ ] Implement agent registration
- [ ] Implement service installation
- [ ] Build MSI package
- [ ] Test installation on clean Windows machine

### Integration
- [ ] Test end-to-end installation
- [ ] Verify agent appears in dashboard
- [ ] Verify telemetry data is received
- [ ] Test uninstallation

---

## File Structure (Final)

```
agent/
├── Cargo.toml
├── src/
│   ├── main.rs
│   ├── config.rs
│   ├── system_info.rs
│   ├── registration.rs
│   ├── tracking.rs
│   ├── api_client.rs
│   └── idle_detection.rs
└── README.md

installer/
├── PrismTrackAgent.wxs
├── Product.wxs
├── CustomActions.wxs
├── build.bat
└── README.md

backend/
└── api/v1/endpoints/
    └── tenant.py (update download-agent endpoint)
```

---

## Next Steps

1. **Start with Backend**: Implement agent download endpoint
2. **Build Rust Agent**: Develop core tracking functionality
3. **Create MSI Installer**: Package everything together
4. **Test & Iterate**: Test on real Windows machines

---

## Notes

- **Security**: Agent token must be stored securely (encrypted file or Windows Credential Manager)
- **Privacy**: Only track basic productivity metrics (window title, process name, idle status)
- **Performance**: Agent should be lightweight (< 10MB, < 1% CPU)
- **Compatibility**: Target Windows 10/11 (64-bit)
- **Service**: Run as Windows Service for persistence

