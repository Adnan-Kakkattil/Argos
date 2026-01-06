# PrismTrack API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1`  
**Authentication:** JWT Bearer Token (except for agent endpoints which use agent tokens)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Platform Admin APIs](#platform-admin-apis)
3. [Tenant Admin APIs](#tenant-admin-apis)
4. [Agent APIs](#agent-apis)
5. [Workflows](#workflows)
6. [Org ID System](#org-id-system)

---

## Authentication

All API endpoints (except agent registration) require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### 1. Platform Admin Login

**Endpoint:** `POST /auth/platform-admin/login`

**Description:** Authenticate platform admin and receive JWT tokens.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Workflow:**
1. Client sends username and password
2. Backend verifies credentials against `platform_admins` table
3. Backend generates JWT access token (expires in configured minutes)
4. Backend generates JWT refresh token
5. Returns both tokens to client

**Error Responses:**
- `401 Unauthorized`: Incorrect username or password

---

### 2. Tenant Admin Login

**Endpoint:** `POST /auth/tenant/login`

**Description:** Authenticate tenant admin and receive JWT tokens.

**Request Body:**
```json
{
  "email": "admin@tenant.com",
  "password": "tenant123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Workflow:**
1. Client sends email and password
2. Backend verifies credentials against `tenants` table
3. Backend generates JWT access token with tenant info
4. Backend generates JWT refresh token
5. Returns both tokens to client

**Error Responses:**
- `401 Unauthorized`: Incorrect email or password

---

### 3. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Description:** Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Workflow:**
1. Client sends refresh token
2. Backend validates refresh token
3. Backend identifies user type (platform_admin or tenant)
4. Backend generates new access and refresh tokens
5. Returns new tokens

**Error Responses:**
- `401 Unauthorized`: Invalid refresh token

---

## Platform Admin APIs

All platform admin endpoints require platform admin authentication.

### 1. List Tenants

**Endpoint:** `GET /platform-admin/tenants`

**Description:** Get paginated list of all tenants in the system.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
{
  "tenants": [
    {
      "id": 1,
      "tenant_org_id": "S18NZD4",
      "name": "Acme Corporation",
      "admin_email": "admin@acme.com",
      "admin_api_key": "abc123...",
      "created_at": "2026-01-01T10:00:00Z",
      "is_active": true
    }
  ],
  "total": 1
}
```

**Workflow:**
1. Platform admin authenticated via JWT
2. Backend queries all tenants from database
3. Returns paginated list

---

### 2. Get Tenant Details

**Endpoint:** `GET /platform-admin/tenants/{tenant_id}`

**Description:** Get detailed information about a specific tenant.

**Path Parameters:**
- `tenant_id` (int): Tenant ID

**Response:**
```json
{
  "id": 1,
  "tenant_org_id": "S18NZD4",
  "name": "Acme Corporation",
  "admin_email": "admin@acme.com",
  "admin_api_key": "abc123...",
  "created_at": "2026-01-01T10:00:00Z",
  "is_active": true
}
```

**Error Responses:**
- `404 Not Found`: Tenant not found

---

### 3. Create Tenant

**Endpoint:** `POST /platform-admin/tenants`

**Description:** Create a new tenant with auto-generated org_id.

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "admin_email": "admin@acme.com",
  "admin_password": "SecurePass123!",
  "company_name": "Acme Corporation",
  "address": "123 Business St, New York, NY 10001",
  "phone": "+1-555-0123",
  "industry_type": "Technology"
}
```

**Response:**
```json
{
  "id": 1,
  "tenant_org_id": "S18NZD4",
  "name": "Acme Corporation",
  "admin_email": "admin@acme.com",
  "admin_api_key": "abc123def456...",
  "created_at": "2026-01-01T10:00:00Z",
  "is_active": true
}
```

**Workflow:**
1. Platform admin sends tenant creation request
2. Backend validates email is unique
3. Backend generates unique `tenant_org_id` (5-8 characters, alphanumeric)
4. Backend hashes admin password using bcrypt
5. Backend generates unique `admin_api_key`
6. Backend creates tenant record in database
7. Returns created tenant with `tenant_org_id` and `admin_api_key`

**Org ID Generation:**
- Length: 5-8 characters
- Format: Alphanumeric (uppercase letters and numbers)
- Uniqueness: Globally unique across all org types
- Example: `S18NZD4`, `ABC123`, `X9K2M`

**Error Responses:**
- `400 Bad Request`: Tenant with this email already exists

---

### 4. Update Tenant

**Endpoint:** `PUT /platform-admin/tenants/{tenant_id}`

**Description:** Update tenant details.

**Path Parameters:**
- `tenant_id` (int): Tenant ID

**Request Body:**
```json
{
  "name": "Acme Corporation Updated",
  "admin_email": "newadmin@acme.com",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 1,
  "tenant_org_id": "S18NZD4",
  "name": "Acme Corporation Updated",
  "admin_email": "newadmin@acme.com",
  "is_active": true
}
```

**Error Responses:**
- `404 Not Found`: Tenant not found
- `400 Bad Request`: Email already in use

---

### 5. Delete Tenant

**Endpoint:** `DELETE /platform-admin/tenants/{tenant_id}`

**Description:** Soft delete (deactivate) a tenant.

**Path Parameters:**
- `tenant_id` (int): Tenant ID

**Response:** `204 No Content`

**Workflow:**
1. Sets `is_active = false` on tenant
2. Tenant and all related data remain in database but are inactive

**Error Responses:**
- `404 Not Found`: Tenant not found

---

### 6. Get Tenant Statistics (Client 360)

**Endpoint:** `GET /platform-admin/tenants/{tenant_id}/stats`

**Description:** Get comprehensive statistics for a tenant (Client 360 view).

**Path Parameters:**
- `tenant_id` (int): Tenant ID

**Response:**
```json
{
  "tenant": {
    "id": 1,
    "tenant_org_id": "S18NZD4",
    "name": "Acme Corporation",
    "admin_email": "admin@acme.com",
    "created_at": "2026-01-01T10:00:00Z",
    "is_active": true
  },
  "statistics": {
    "companies": 5,
    "branches": 12,
    "users": 25,
    "agents": 8
  }
}
```

**Workflow:**
1. Gets tenant details
2. Counts active companies for tenant
3. Counts active branches (through companies)
4. Counts active users for tenant
5. Counts agents with matching `tenant_org_id`
6. Returns aggregated statistics

---

## Tenant Admin APIs

All tenant admin endpoints require tenant authentication and automatically scope to the authenticated tenant.

### Company Management

#### 1. List Companies

**Endpoint:** `GET /tenant/companies`

**Description:** List all companies for the current tenant.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
{
  "companies": [
    {
      "id": 1,
      "company_org_id": "6CVQAG",
      "name": "Test Company",
      "tenant_id": 1,
      "is_active": true
    }
  ],
  "total": 1
}
```

---

#### 2. Get Company Details

**Endpoint:** `GET /tenant/companies/{company_id}`

**Description:** Get company details (must belong to tenant).

**Path Parameters:**
- `company_id` (int): Company ID

**Response:**
```json
{
  "id": 1,
  "company_org_id": "6CVQAG",
  "name": "Test Company",
  "tenant_id": 1,
  "is_active": true
}
```

**Error Responses:**
- `404 Not Found`: Company not found or doesn't belong to tenant

---

#### 3. Create Company

**Endpoint:** `POST /tenant/companies`

**Description:** Create a new company with auto-generated org_id.

**Request Body:**
```json
{
  "name": "Test Company"
}
```

**Response:**
```json
{
  "id": 1,
  "company_org_id": "6CVQAG",
  "name": "Test Company",
  "tenant_id": 1,
  "is_active": true
}
```

**Workflow:**
1. Tenant admin sends company creation request
2. Backend generates unique `company_org_id` (5-8 characters)
3. Backend creates company linked to current tenant
4. Returns created company with `company_org_id`

**Org ID Generation:**
- Same format as tenant org_id
- Globally unique across all org types
- Example: `6CVQAG`, `XYZ789`

---

#### 4. Update Company

**Endpoint:** `PUT /tenant/companies/{company_id}`

**Description:** Update company details.

**Request Body:**
```json
{
  "name": "Updated Company Name"
}
```

**Response:**
```json
{
  "id": 1,
  "company_org_id": "6CVQAG",
  "name": "Updated Company Name",
  "tenant_id": 1,
  "is_active": true
}
```

---

#### 5. Delete Company

**Endpoint:** `DELETE /tenant/companies/{company_id}`

**Description:** Soft delete (deactivate) a company.

**Response:** `204 No Content`

---

### Branch Management

#### 1. List Branches

**Endpoint:** `GET /tenant/companies/{company_id}/branches`

**Description:** List all branches for a company.

**Response:**
```json
{
  "branches": [
    {
      "id": 1,
      "branch_org_id": "3CDWA",
      "name": "Test Branch",
      "location": "New York, NY",
      "ip_addresses": "192.168.1.1,192.168.1.2",
      "company_id": 1,
      "is_active": true
    }
  ],
  "total": 1
}
```

---

#### 2. Create Branch

**Endpoint:** `POST /tenant/companies/{company_id}/branches`

**Description:** Create a new branch with auto-generated org_id.

**Request Body:**
```json
{
  "name": "Test Branch",
  "location": "New York, NY",
  "ip_addresses": "192.168.1.1,192.168.1.2"
}
```

**Response:**
```json
{
  "id": 1,
  "branch_org_id": "3CDWA",
  "name": "Test Branch",
  "location": "New York, NY",
  "ip_addresses": "192.168.1.1,192.168.1.2",
  "company_id": 1,
  "is_active": true
}
```

**Workflow:**
1. Tenant admin sends branch creation request
2. Backend generates unique `branch_org_id` (5-8 characters)
3. Backend creates branch linked to company
4. Returns created branch with `branch_org_id`

---

### User Management

#### 1. List Users

**Endpoint:** `GET /tenant/users`

**Description:** List all users for the current tenant.

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "john.doe",
      "email": "john@tenant.com",
      "role": "admin",
      "tenant_id": 1,
      "is_active": true
    }
  ],
  "total": 1
}
```

---

#### 2. Create User

**Endpoint:** `POST /tenant/users`

**Description:** Create a new user for the tenant.

**Request Body:**
```json
{
  "username": "john.doe",
  "email": "john@tenant.com",
  "password": "SecurePass123!",
  "role": "admin"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "john.doe",
  "email": "john@tenant.com",
  "role": "admin",
  "tenant_id": 1,
  "is_active": true
}
```

---

### Agent Management

#### 1. List Agents

**Endpoint:** `GET /tenant/agents`

**Description:** List all agents for the current tenant (includes agents for tenant, companies, and branches).

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
{
  "agents": [
    {
      "id": 17,
      "org_id": "S18NZD4",
      "org_type": "TENANT",
      "machine_name": "GRIT-CLT-LT-246",
      "hardware_uuid": "210ea27c-215e-434e-8489-cc9bed...",
      "status": "ONLINE",
      "last_seen": "2026-01-02T11:14:11Z",
      "registered_at": "2026-01-02T16:10:42Z"
    }
  ],
  "total": 1
}
```

**Workflow:**
1. Gets tenant's `tenant_org_id`
2. Gets all company `company_org_id`s for tenant
3. Gets all branch `branch_org_id`s for tenant
4. Queries agents matching any of these org_ids
5. Returns list of agents

---

#### 2. Get Agent Details

**Endpoint:** `GET /tenant/agents/{agent_id}`

**Description:** Get detailed information about a specific agent (must belong to tenant).

**Response:**
```json
{
  "id": 17,
  "org_id": "S18NZD4",
  "org_type": "TENANT",
  "machine_name": "GRIT-CLT-LT-246",
  "hardware_uuid": "210ea27c-215e-434e-8489-cc9bed...",
  "status": "ONLINE",
  "last_seen": "2026-01-02T11:14:11Z",
  "registered_at": "2026-01-02T16:10:42Z"
}
```

---

#### 3. Get Agent Telemetry

**Endpoint:** `GET /tenant/agents/{agent_id}/telemetry`

**Description:** Get telemetry data for a specific agent.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
{
  "agent_id": 17,
  "telemetry": [
    {
      "id": 1,
      "window_title": "PrismTrack - Employee Tracking System",
      "process_name": "chrome.exe",
      "timestamp": "2026-01-02T11:13:12Z",
      "is_idle": false
    }
  ],
  "total": 1
}
```

---

#### 4. List Org IDs

**Endpoint:** `GET /tenant/org-ids`

**Description:** List all org_ids available for agent download (tenant, companies, branches).

**Response:**
```json
{
  "tenant": {
    "org_id": "S18NZD4",
    "type": "tenant",
    "name": "Test Corporation",
    "id": 1
  },
  "companies": [
    {
      "org_id": "6CVQAG",
      "type": "company",
      "name": "Test Company",
      "id": 1
    }
  ],
  "branches": [
    {
      "org_id": "3CDWA",
      "type": "branch",
      "name": "Test Branch",
      "id": 1,
      "company_id": 1
    }
  ],
  "total": 3
}
```

**Workflow:**
1. Gets tenant org_id
2. Gets all company org_ids for tenant
3. Gets all branch org_ids for tenant
4. Returns organized list

---

#### 5. Download Agent MSI

**Endpoint:** `GET /tenant/download-agent/{org_id}`

**Description:** Download MSI installer for a specific org_id.

**Path Parameters:**
- `org_id` (string): Org ID (tenant, company, or branch)

**Response:** Binary file (MSI installer)

**Headers:**
- `Content-Disposition: attachment; filename="PrismTrack_Agent_{org_id}.msi"`
- `Content-Type: application/octet-stream`

**Workflow:**
1. Validates org_id belongs to tenant
2. Checks if org_id is tenant, company, or branch org_id
3. Verifies org_id is active
4. Serves MSI file from `backend/static/agents/PrismTrackAgent.msi`
5. Returns file with org_id in filename

**Error Responses:**
- `404 Not Found`: Org ID not found or doesn't belong to tenant
- `500 Internal Server Error`: MSI file not found

---

## Agent APIs

Agent APIs use agent tokens (not JWT) for authentication via `X-Agent-Token` header.

### 1. Register Agent

**Endpoint:** `POST /agent/register`

**Description:** Register a new agent with the backend. This is the first step when installing an agent.

**Request Body:**
```json
{
  "org_id": "S18NZD4",
  "org_type": "TENANT",
  "machine_name": "GRIT-CLT-LT-246",
  "hardware_uuid": "210ea27c-215e-434e-8489-cc9bed..."
}
```

**Response:**
```json
{
  "agent_id": 17,
  "agent_token": "7cdJWFA2GXSlOvFTjTwODyKEAMDKhOTfBqph3rEJwkQ",
  "message": "Agent registered successfully"
}
```

**Workflow:**
1. Agent collects system information (hardware UUID, machine name)
2. Agent sends registration request with org_id
3. Backend validates org_id exists (checks tenant, company, branch tables)
4. Backend determines org_type automatically
5. Backend checks if agent with same hardware_uuid exists:
   - If exists: Updates existing agent and returns existing token
   - If new: Generates unique agent_token
6. Backend creates agent record in database
7. Returns agent_id and agent_token
8. Agent saves token to config.json for future use

**Org ID Validation:**
- Checks `tenants.tenant_org_id`
- Checks `companies.company_org_id`
- Checks `branches.branch_org_id`
- Must be active (`is_active = true`)

**Error Responses:**
- `404 Not Found`: Invalid org_id (not found or inactive)

---

### 2. Agent Heartbeat

**Endpoint:** `POST /agent/heartbeat`

**Description:** Agent sends periodic heartbeat to indicate it's online.

**Headers:**
- `X-Agent-Token: <agent_token>` (required)

**Request Body:**
```json
{
  "agent_token": "7cdJWFA2GXSlOvFTjTwODyKEAMDKhOTfBqph3rEJwkQ",
  "status": "ONLINE"
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Heartbeat received",
  "timestamp": "2026-01-02T16:45:00Z"
}
```

**Workflow:**
1. Agent sends heartbeat every 30 seconds (configurable)
2. Backend verifies agent_token from header
3. Backend updates agent's `last_seen` timestamp
4. Backend updates agent's `status` to ONLINE
5. Returns success response

**Error Responses:**
- `401 Unauthorized`: Invalid agent token

---

### 3. Submit Telemetry

**Endpoint:** `POST /agent/telemetry`

**Description:** Agent submits productivity tracking data.

**Headers:**
- `X-Agent-Token: <agent_token>` (required)

**Request Body:**
```json
{
  "agent_token": "7cdJWFA2GXSlOvFTjTwODyKEAMDKhOTfBqph3rEJwkQ",
  "telemetry": [
    {
      "window_title": "PrismTrack - Employee Tracking System",
      "process_name": "chrome.exe",
      "timestamp": "2026-01-02T16:45:00Z",
      "is_idle": false,
      "screenshot_url": null
    }
  ]
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Telemetry data received: 1 records",
  "records_count": 1,
  "timestamp": "2026-01-02T16:45:00Z"
}
```

**Workflow:**
1. Agent collects productivity data every 30 seconds:
   - Active window title
   - Process name
   - Timestamp
   - Idle status (true if no input for 5+ minutes)
2. Agent sends telemetry data array
3. Backend verifies agent_token from header
4. Backend creates telemetry records in database
5. Backend updates agent's `last_seen` timestamp
6. Backend updates agent's `status` to ONLINE
7. Returns success response

**Telemetry Data:**
- `window_title`: Title of active window
- `process_name`: Name of process (e.g., "chrome.exe")
- `timestamp`: UTC timestamp
- `is_idle`: Boolean (true if user idle for threshold duration)
- `screenshot_url`: Optional screenshot URL (future feature)

**Error Responses:**
- `401 Unauthorized`: Invalid agent token or token mismatch

---

### 4. List Agents (Admin)

**Endpoint:** `GET /agent/agents`

**Description:** List all agents (for platform/tenant admin use, no authentication required for now).

**Query Parameters:**
- `org_id` (string, optional): Filter by org_id
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum number of records to return

**Response:**
```json
{
  "agents": [
    {
      "id": 17,
      "org_id": "S18NZD4",
      "org_type": "TENANT",
      "machine_name": "GRIT-CLT-LT-246",
      "hardware_uuid": "210ea27c-215e-434e-8489-cc9bed...",
      "status": "ONLINE",
      "last_seen": "2026-01-02T11:14:11Z"
    }
  ],
  "total": 1
}
```

---

### 5. Get Agent Details (Admin)

**Endpoint:** `GET /agent/agents/{agent_id}`

**Description:** Get agent details by ID.

**Response:**
```json
{
  "id": 17,
  "org_id": "S18NZD4",
  "org_type": "TENANT",
  "machine_name": "GRIT-CLT-LT-246",
  "hardware_uuid": "210ea27c-215e-434e-8489-cc9bed...",
  "status": "ONLINE",
  "last_seen": "2026-01-02T11:14:11Z",
  "registered_at": "2026-01-02T16:10:42Z"
}
```

---

## Workflows

### Complete Tenant Creation Workflow

1. **Platform Admin Login**
   - `POST /auth/platform-admin/login`
   - Receive JWT tokens

2. **Create Tenant**
   - `POST /platform-admin/tenants`
   - Backend generates `tenant_org_id` (e.g., "S18NZD4")
   - Backend hashes password
   - Backend generates `admin_api_key`
   - Returns tenant with credentials

3. **Tenant Admin Login**
   - `POST /auth/tenant/login`
   - Use tenant admin email and password
   - Receive JWT tokens

4. **Create Company (Optional)**
   - `POST /tenant/companies`
   - Backend generates `company_org_id` (e.g., "6CVQAG")

5. **Create Branch (Optional)**
   - `POST /tenant/companies/{company_id}/branches`
   - Backend generates `branch_org_id` (e.g., "3CDWA")

6. **Download Agent MSI**
   - `GET /tenant/download-agent/{org_id}`
   - Download MSI for tenant, company, or branch org_id

---

### Complete Agent Installation Workflow

1. **Download MSI**
   - Tenant admin downloads MSI from dashboard
   - `GET /tenant/download-agent/{org_id}`
   - MSI file: `PrismTrack_Agent_{org_id}.msi`

2. **Install MSI**
   - User runs MSI installer on Windows machine
   - MSI extracts files to `C:\Program Files\PrismTrack\Agent\`
   - MSI runs `installer_script.ps1`

3. **Installer Script Execution**
   - Collects system information:
     - Hardware UUID (from Windows registry)
     - Machine name
     - Username
     - Hostname
     - UPN email
   - Updates `config.json` with org_id
   - Registers agent: `POST /agent/register`
   - Receives `agent_token`
   - Saves token to `config.json`
   - Starts `PrismTrackAgent.exe`

4. **Agent Registration**
   - Agent reads `config.json`
   - If no `agent_token`, calls `POST /agent/register`
   - Receives `agent_token`
   - Saves token to `config.json`

5. **Agent Running**
   - Agent starts main loop:
     - **Heartbeat Loop** (every 30 seconds):
       - `POST /agent/heartbeat`
       - Updates `last_seen` and `status`
     - **Telemetry Loop** (every 30 seconds):
       - Collects active window title
       - Collects process name
       - Checks idle status
       - `POST /agent/telemetry`
       - Sends telemetry data array

6. **View Data**
   - Tenant admin views agents: `GET /tenant/agents`
   - View telemetry: `GET /tenant/agents/{agent_id}/telemetry`

---

## Org ID System

### Overview

Org IDs are unique identifiers (5-8 characters, alphanumeric) used to identify tenants, companies, and branches. They are used for:
- Agent installation and registration
- Agent-to-org association
- Agent download identification

### Org ID Types

1. **Tenant Org ID** (`tenant_org_id`)
   - Generated when tenant is created
   - Example: `S18NZD4`
   - Used for tenant-level agent installation

2. **Company Org ID** (`company_org_id`)
   - Generated when company is created
   - Example: `6CVQAG`
   - Used for company-specific agent installation

3. **Branch Org ID** (`branch_org_id`)
   - Generated when branch is created
   - Example: `3CDWA`
   - Used for branch-specific agent installation

### Org ID Generation

- **Length**: 5-8 characters (random)
- **Format**: Uppercase letters (A-Z) and numbers (0-9)
- **Uniqueness**: Globally unique across all org types
- **Generation**: Uses `generate_org_id()` utility function
- **Validation**: Checked against database for uniqueness

### Org ID Usage

1. **Agent Registration**
   - Agent sends `org_id` during registration
   - Backend validates org_id exists and is active
   - Backend determines `org_type` automatically

2. **Agent Download**
   - Tenant admin selects org_id (tenant, company, or branch)
   - Backend validates org_id belongs to tenant
   - Backend serves MSI with org_id in filename

3. **Agent Association**
   - Agent is associated with org_id in database
   - Tenant admin can view all agents for their org_ids
   - Telemetry data is linked to agent and org_id

---

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Common Error Responses

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

Currently, there are no rate limits implemented. For production, consider implementing:
- Authentication endpoints: 5 requests per minute
- Agent endpoints: 100 requests per minute
- Admin endpoints: 60 requests per minute

---

## API Versioning

Current version: **v1**

Base URL: `/api/v1`

Future versions will use `/api/v2`, `/api/v3`, etc.

---

## Additional Resources

- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `GET /health`
- **Root**: `GET /` (API info)

---

## Notes

- All timestamps are in UTC (ISO 8601 format)
- All passwords are hashed using bcrypt
- Agent tokens are randomly generated 32-character strings
- Org IDs are case-sensitive
- All soft deletes set `is_active = false` (data remains in database)

---

**Last Updated:** 2026-01-02  
**API Version:** 1.0.0




