# Agent Files Directory

This directory contains the agent files served by the backend:

- `PrismTrackAgent.msi` - MSI installer for PrismTrack Agent
- `PrismTrackAgent.exe` - Python executable (packaged with PyInstaller)

## Setup

Copy the following files to this directory:

1. From `installer/PrismTrackAgent.msi` → `backend/static/agents/PrismTrackAgent.msi`
2. From `PrismTrackAgent/dist/PrismTrackAgent.exe` → `backend/static/agents/PrismTrackAgent.exe`

## Usage

The backend serves these files via:
- `/static/agents/PrismTrackAgent.msi` - Direct access to MSI
- `/api/v1/tenant/download-agent/{org_id}` - Download endpoint with org_id validation

## Notes

- The MSI installer includes `installer_script.ps1` which configures the agent with the org_id
- The installer script collects system information and registers the agent with the backend
- After installation, the agent starts tracking productivity automatically

