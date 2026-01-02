# PrismTrack Agent MSI Installer

Windows MSI installer for PrismTrack Agent that:
1. Downloads agent.zip from backend
2. Extracts PrismTrackAgent.exe and config.json
3. Collects system information
4. Registers agent with backend
5. Installs and runs PrismTrackAgent.exe

## Requirements

- Windows 10/11
- WiX Toolset 3.11+ (for building MSI)
- OR Python with msilib (for Python-based MSI creation)

## Installation Methods

### Method 1: WiX Toolset (Recommended)

1. Install WiX Toolset from: https://wixtoolset.org/
2. Build MSI:
   ```bash
   candle PrismTrackAgent.wxs
   light PrismTrackAgent.wixobj -out PrismTrackAgent.msi
   ```

### Method 2: Python msilib (Simpler)

1. Run build script:
   ```bash
   python create_msi.py
   ```

## MSI Installer Workflow

1. **Pre-Installation Checks**
   - Verify Windows version
   - Check admin privileges
   - Check if agent already installed

2. **Download Agent Package**
   - Download agent.zip from: `{API_BASE}/api/v1/tenant/download-agent-package/{org_id}`
   - Save to: `%TEMP%\PrismTrackAgent.zip`

3. **Extract Agent Package**
   - Extract to: `C:\Program Files\PrismTrack\Agent\`
   - Files: `PrismTrackAgent.exe`, `config.json`

4. **Collect System Information**
   - Hardware UUID (from registry)
   - Machine name
   - Username
   - Hostname
   - UPN email

5. **Register Agent**
   - Call: `POST /api/v1/agent/register`
   - Save agent_token to config.json

6. **Install as Service** (Optional)
   - Install PrismTrackAgent.exe as Windows Service
   - Set to auto-start

7. **Post-Installation**
   - Show completion message
   - Create desktop shortcut (optional)

## Files

- `PrismTrackAgent.wxs` - WiX source file
- `create_msi.py` - Python script to create MSI
- `installer_script.ps1` - PowerShell installation script
- `build_msi.bat` - Build script for MSI

