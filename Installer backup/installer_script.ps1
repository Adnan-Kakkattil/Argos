# PrismTrack Agent Installation Script
# This script is called by the MSI installer to:
# 1. Download agent.zip from backend
# 2. Extract and install PrismTrackAgent.exe
# 3. Collect system information
# 4. Register agent with backend
# 5. Start the agent

param(
    [Parameter(Mandatory=$false)]
    [string]$OrgId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ApiBase = "http://localhost:8000/api/v1",
    
    [Parameter(Mandatory=$false)]
    [string]$InstallDir = "C:\Program Files\PrismTrack\Agent"
)

# If org_id not provided, try to extract from config.json
$configPath = Join-Path $InstallDir "config.json"
if ([string]::IsNullOrEmpty($OrgId) -and (Test-Path $configPath)) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        if ($config.org_id -and $config.org_id -ne "YOUR_ORG_ID_HERE" -and $config.org_id -ne "") {
            $OrgId = $config.org_id
            Write-Host "  Using org_id from config.json: $OrgId" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Could not read org_id from config.json" -ForegroundColor Yellow
    }
}

# If still empty, show warning
if ([string]::IsNullOrEmpty($OrgId)) {
    Write-Host "  WARNING: org_id not provided!" -ForegroundColor Yellow
    Write-Host "  The agent will need to be configured manually." -ForegroundColor Yellow
    Write-Host "  Please update config.json with the correct org_id after installation." -ForegroundColor Yellow
    Write-Host "  The org_id should match the one used when downloading the MSI installer." -ForegroundColor Yellow
}

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PrismTrack Agent Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create installation directory
Write-Host "[1/5] Creating installation directory..." -ForegroundColor Yellow
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
Write-Host "  Directory: $InstallDir" -ForegroundColor Green
Write-Host ""

# Step 2: Collect System Information
Write-Host "[2/5] Collecting system information..." -ForegroundColor Yellow

# Get Hardware UUID from registry
try {
    $machineGuid = (Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Cryptography" -Name "MachineGuid").MachineGuid
    Write-Host "  Hardware UUID: $machineGuid" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not get Hardware UUID" -ForegroundColor Yellow
    $machineGuid = [System.Guid]::NewGuid().ToString()
}

# Get Machine Name
$machineName = $env:COMPUTERNAME
Write-Host "  Machine Name: $machineName" -ForegroundColor Green

# Get Username
$username = $env:USERNAME
$domain = $env:USERDOMAIN
$fullUsername = "$domain\$username"
Write-Host "  Username: $fullUsername" -ForegroundColor Green

# Get Hostname
$hostname = [System.Net.Dns]::GetHostByName($env:COMPUTERNAME).HostName
Write-Host "  Hostname: $hostname" -ForegroundColor Green

# Get UPN Email (try AD first)
$upnEmail = $null
try {
    $adUser = Get-ADUser -Identity $username -Properties UserPrincipalName -ErrorAction SilentlyContinue
    if ($adUser -and $adUser.UserPrincipalName) {
        $upnEmail = $adUser.UserPrincipalName
    }
} catch {
    # Not in AD domain, use local account
    $upnEmail = "$username@$hostname"
}
Write-Host "  UPN Email: $upnEmail" -ForegroundColor Green
Write-Host ""

# Step 3: Download Agent Package (if not already present)
Write-Host "[3/5] Checking agent package..." -ForegroundColor Yellow
$agentExePath = Join-Path $InstallDir "PrismTrackAgent.exe"
$configPath = Join-Path $InstallDir "config.json"

if (-not (Test-Path $agentExePath)) {
    Write-Host "  Agent executable not found. Please ensure PrismTrackAgent.exe is in the MSI package." -ForegroundColor Red
    exit 1
}

Write-Host "  Agent executable found: $agentExePath" -ForegroundColor Green
Write-Host ""

# Step 4: Create/Update config.json
Write-Host "[4/5] Creating configuration..." -ForegroundColor Yellow

# Load existing config.json if it exists, otherwise create new
$config = @{
    org_id = $OrgId
    api_base = $ApiBase
    agent_token = $null
    heartbeat_interval = 30
    telemetry_interval = 30
    idle_threshold_seconds = 300
}

# If config.json exists, load it and update org_id
if (Test-Path $configPath) {
    try {
        $existingConfig = Get-Content $configPath | ConvertFrom-Json
        $config.org_id = if ([string]::IsNullOrEmpty($OrgId)) { $existingConfig.org_id } else { $OrgId }
        $config.api_base = if ($existingConfig.api_base) { $existingConfig.api_base } else { $ApiBase }
        $config.agent_token = $existingConfig.agent_token
        $config.heartbeat_interval = if ($existingConfig.heartbeat_interval) { $existingConfig.heartbeat_interval } else { 30 }
        $config.telemetry_interval = if ($existingConfig.telemetry_interval) { $existingConfig.telemetry_interval } else { 30 }
        $config.idle_threshold_seconds = if ($existingConfig.idle_threshold_seconds) { $existingConfig.idle_threshold_seconds } else { 300 }
    } catch {
        Write-Host "  Could not load existing config, creating new one" -ForegroundColor Yellow
    }
}

# Validate org_id
if ([string]::IsNullOrEmpty($config.org_id) -or $config.org_id -eq "YOUR_ORG_ID_HERE") {
    Write-Host "  ERROR: org_id is required but not provided!" -ForegroundColor Red
    Write-Host "  Please update config.json manually with the correct org_id." -ForegroundColor Yellow
    Write-Host "  The org_id should match the one used when downloading the MSI installer." -ForegroundColor Yellow
} else {
    Write-Host "  Using org_id: $($config.org_id)" -ForegroundColor Green
}

$config | ConvertTo-Json -Depth 10 | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "  Configuration saved: $configPath" -ForegroundColor Green
Write-Host ""

# Step 5: Register Agent with Backend
Write-Host "[5/5] Registering agent with backend..." -ForegroundColor Yellow
$registerUrl = "$ApiBase/agent/register"

$registerPayload = @{
    org_id = $OrgId
    org_type = "TENANT"
    machine_name = $machineName
    hardware_uuid = $machineGuid
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri $registerUrl -Method POST -Body $registerPayload -ContentType "application/json" -ErrorAction Stop
    
    $agentToken = $response.agent_token
    $agentId = $response.agent_id
    
    Write-Host "  Agent registered successfully!" -ForegroundColor Green
    Write-Host "  Agent ID: $agentId" -ForegroundColor Green
    
    # Update config.json with agent token
    $configObj = Get-Content $configPath | ConvertFrom-Json
    $configObj.agent_token = $agentToken
    $configObj | ConvertTo-Json -Depth 10 | Out-File -FilePath $configPath -Encoding UTF8
    
    Write-Host "  Agent token saved to config.json" -ForegroundColor Green
    
} catch {
    Write-Host "  Warning: Failed to register agent: $_" -ForegroundColor Yellow
    Write-Host "  Agent will attempt to register on first run." -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Start Agent (Optional - as background process)
Write-Host "Starting PrismTrack Agent..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath $agentExePath -WorkingDirectory $InstallDir -WindowStyle Hidden -PassThru
    Write-Host "  Agent started (PID: $($process.Id))" -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not start agent automatically: $_" -ForegroundColor Yellow
    Write-Host "  Please start the agent manually from: $agentExePath" -ForegroundColor Yellow
}
Write-Host ""

# Installation Complete
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PrismTrack Agent has been installed to:" -ForegroundColor White
Write-Host "  $InstallDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "The agent is now tracking productivity and sending data to:" -ForegroundColor White
Write-Host "  $ApiBase" -ForegroundColor Cyan
Write-Host ""

