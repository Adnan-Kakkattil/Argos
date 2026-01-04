# Agent Version Management System

## Overview

The PrismTrack system now includes a comprehensive version management system that allows platform admins to upload new agent versions, and agents automatically check for and install updates without user interaction.

## Features

1. **Version Upload**: Platform admins can upload new agent versions with version number, changelog, and ZIP file
2. **Automatic Update Check**: Agents periodically check for new versions (default: every hour)
3. **Automatic Download**: When a new version is available, agents automatically download it
4. **Automatic Installation**: Agents extract and install the update, preserving configuration
5. **Automatic Restart**: Agents restart with the new version after successful update
6. **Integrity Verification**: File hash verification ensures update integrity
7. **Backup & Rollback**: Current version is backed up before update, with automatic rollback on failure

## Database Schema

### agent_versions Table

```sql
CREATE TABLE agent_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    version_number VARCHAR(50) UNIQUE NOT NULL,
    changelog TEXT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64),  -- SHA-256 hash
    is_active BOOLEAN DEFAULT TRUE,
    is_latest BOOLEAN DEFAULT FALSE,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP NULL
);
```

### agents Table Update

Added `current_version` column to track which version each agent is running:

```sql
ALTER TABLE agents ADD COLUMN current_version VARCHAR(50);
```

## API Endpoints

### Platform Admin Endpoints

#### 1. List Versions
- **Endpoint**: `GET /api/v1/version/versions`
- **Auth**: Platform Admin
- **Response**: List of all agent versions

#### 2. Get Version Details
- **Endpoint**: `GET /api/v1/version/versions/{version_id}`
- **Auth**: Platform Admin
- **Response**: Version details

#### 3. Create Version
- **Endpoint**: `POST /api/v1/version/versions`
- **Auth**: Platform Admin
- **Request**: Multipart form data
  - `version_number`: Version string (e.g., "1.0.1")
  - `changelog`: Description of changes
  - `file`: ZIP file containing agent files
- **Response**: Created version object

#### 4. Update Version
- **Endpoint**: `PUT /api/v1/version/versions/{version_id}`
- **Auth**: Platform Admin
- **Request**: JSON with optional fields
  - `version_number`, `changelog`, `is_active`, `is_latest`, `released_at`
- **Response**: Updated version object

#### 5. Delete Version
- **Endpoint**: `DELETE /api/v1/version/versions/{version_id}`
- **Auth**: Platform Admin
- **Action**: Soft delete (sets `is_active = false`)

### Agent Endpoints

#### 1. Check for Updates
- **Endpoint**: `GET /api/v1/version/agent/check-update?current_version={version}`
- **Auth**: Agent Token (optional, via `X-Agent-Token` header)
- **Response**: 
  ```json
  {
    "update_available": true,
    "current_version": "1.0.0",
    "latest_version": "1.0.1",
    "changelog": "Bug fixes and improvements",
    "download_url": "/static/agents/versions/agent_v1.0.1.zip",
    "file_size": 5242880,
    "file_hash": "abc123..."
  }
  ```

#### 2. Download Update
- **Endpoint**: `GET /api/v1/version/agent/download-update/{version_number}`
- **Auth**: Agent Token (optional, via `X-Agent-Token` header)
- **Response**: ZIP file download
- **Headers**: 
  - `X-Version-Number`: Version number
  - `X-File-Hash`: SHA-256 hash
  - `X-File-Size`: File size in bytes

## Agent Update Process

### 1. Update Checker

The agent includes an `UpdateChecker` class (`PrismTrackAgent/update_checker.py`) that:

- Checks for updates periodically (configurable interval, default: 1 hour)
- Downloads update ZIP file
- Verifies file integrity using SHA-256 hash
- Extracts and applies update
- Creates backup of current version
- Restores from backup if update fails
- Restarts agent with new version

### 2. Configuration

Agent `config.json` now includes:

```json
{
  "current_version": "1.0.0",
  "update_check_interval": 3600
}
```

- `current_version`: Current agent version
- `update_check_interval`: Seconds between update checks (default: 3600 = 1 hour)

### 3. Update Workflow

1. **Check for Updates** (every hour):
   - Agent calls `/version/agent/check-update` with current version
   - Backend compares with latest version
   - Returns update info if newer version available

2. **Download Update**:
   - Agent downloads ZIP file from download URL
   - Verifies file hash matches expected hash
   - Saves to temporary directory

3. **Apply Update**:
   - Creates backup of current version (config.json, executable)
   - Extracts ZIP to temporary directory
   - Copies new files to agent directory
   - Preserves config.json (restores from backup)
   - Cleans up temporary files

4. **Restart Agent**:
   - Starts new agent process
   - Exits current process
   - New version runs with updated code

### 4. Error Handling

- **Download Failure**: Agent continues running, will retry on next check
- **Hash Mismatch**: Update is rejected, file deleted
- **Extraction Failure**: Backup is restored, agent continues with current version
- **Update Failure**: Automatic rollback to previous version

## Frontend UI

### Platform Admin Dashboard

- **"Manage Versions"** button in platform admin dashboard
- **Version List**: Shows all versions with:
  - Version number
  - Changelog preview
  - File size
  - Status (Active/Inactive)
  - Latest badge
  - Created date
  - Delete action

### Upload New Version

- **Form Fields**:
  - Version Number (e.g., "1.0.1")
  - Changelog (text area)
  - ZIP File upload
- **Validation**: 
  - Version number must be unique
  - File must be .zip format
  - All fields required

## File Structure

```
backend/
├── static/
│   └── agents/
│       └── versions/          # Version ZIP files stored here
│           └── agent_v1.0.1.zip
├── models/
│   └── agent_version.py       # AgentVersion model
├── schemas/
│   └── agent_version.py      # Version schemas
└── api/v1/endpoints/
    └── version.py             # Version management endpoints

PrismTrackAgent/
├── update_checker.py          # Update checker and installer
├── config.json                # Now includes current_version
└── main.py                    # Includes update check in main loop
```

## Usage

### For Platform Admins

1. **Upload New Version**:
   - Login as platform admin
   - Click "Manage Versions"
   - Click "Upload New Version"
   - Enter version number (e.g., "1.0.1")
   - Enter changelog
   - Select ZIP file containing agent files
   - Click "Upload Version"

2. **Manage Versions**:
   - View all versions
   - Delete inactive versions
   - Mark versions as latest (automatic when uploading)

### For Agents

Agents automatically:
- Check for updates every hour
- Download and install new versions
- Restart with new version
- No user interaction required

## Security

- **File Integrity**: SHA-256 hash verification
- **Authentication**: Agent token required for update endpoints
- **Authorization**: Only platform admins can upload versions
- **Backup**: Automatic backup before update
- **Rollback**: Automatic rollback on failure

## Best Practices

1. **Version Numbering**: Use semantic versioning (e.g., 1.0.1, 2.0.0)
2. **Changelog**: Provide clear, detailed changelog for each version
3. **Testing**: Test updates thoroughly before uploading
4. **ZIP Structure**: Ensure ZIP contains all necessary files
5. **Config Preservation**: Agent automatically preserves config.json

## Migration

To add version management to existing database:

```sql
-- Run database/migrations/add_agent_versions.sql
SOURCE database/migrations/add_agent_versions.sql;
```

## Future Enhancements

- Version rollback from admin UI
- Update scheduling (deploy updates at specific times)
- Update notifications
- Version comparison view
- Update statistics (how many agents updated, etc.)

