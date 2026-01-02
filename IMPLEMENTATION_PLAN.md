# PrismTrack - Employee Tracking System
## Multi-Tenant Enterprise Implementation Plan

### Project Overview
PrismTrack is a multi-tenant employee monitoring system where a Platform Admin (Superadmin) creates tenants, and each tenant can manage multiple companies and branches. Each organization level (tenant, company, branch) gets a unique Org ID for agent installation and tracking.

---

## Architecture Overview

### System Hierarchy
```
Platform Admin (Superadmin)
    └── Tenants (with Tenant Org ID: 5-8 chars)
        └── Companies (with Company Org ID: 5-8 chars)
            └── Branches (with Branch Org ID: 5-8 chars)
                └── Agents (installed per Org ID)
```

### Technology Stack
- **Backend**: Python FastAPI
- **Database**: MySQL
- **Frontend**: HTML5 (with Tailwind CSS)
- **Agent**: Rust
- **Installer**: MSI (WiX Toolset)

---

## Phase 1: Database Schema & Backend Foundation

### 1.1 Database Schema Design

#### `platform_admins` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- username (VARCHAR(100), UNIQUE)
- email (VARCHAR(255), UNIQUE)
- password_hash (VARCHAR(255))
- created_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT TRUE)
```

#### `tenants` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- tenant_org_id (VARCHAR(8), UNIQUE) -- 5-8 character unique ID
- name (VARCHAR(255))
- admin_email (VARCHAR(255))
- admin_password_hash (VARCHAR(255))
- admin_api_key (VARCHAR(255), UNIQUE)
- created_by (INT, FOREIGN KEY -> platform_admins.id)
- created_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT TRUE)
```

#### `companies` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- tenant_id (INT, FOREIGN KEY -> tenants.id)
- company_org_id (VARCHAR(8), UNIQUE) -- 5-8 character unique ID
- name (VARCHAR(255))
- created_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT TRUE)
```

#### `branches` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- company_id (INT, FOREIGN KEY -> companies.id)
- branch_org_id (VARCHAR(8), UNIQUE) -- 5-8 character unique ID
- name (VARCHAR(255))
- location (VARCHAR(255))
- ip_addresses (TEXT) -- JSON array of IPs
- created_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT TRUE)
```

#### `users` Table (Client Admin Users)
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- tenant_id (INT, FOREIGN KEY -> tenants.id)
- username (VARCHAR(100))
- email (VARCHAR(255), UNIQUE)
- password_hash (VARCHAR(255))
- role (VARCHAR(50)) -- 'admin', 'manager', 'viewer'
- created_at (TIMESTAMP)
- is_active (BOOLEAN, DEFAULT TRUE)
```

#### `agents` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- org_id (VARCHAR(8)) -- Can be tenant_org_id, company_org_id, or branch_org_id
- org_type (ENUM('tenant', 'company', 'branch'))
- machine_name (VARCHAR(255))
- hardware_uuid (VARCHAR(255), UNIQUE)
- agent_token (VARCHAR(255), UNIQUE)
- last_seen (TIMESTAMP)
- status (ENUM('online', 'offline'))
- registered_at (TIMESTAMP)
```

#### `telemetry` Table
```sql
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- agent_id (INT, FOREIGN KEY -> agents.id)
- window_title (VARCHAR(500))
- process_name (VARCHAR(255))
- timestamp (TIMESTAMP)
- is_idle (BOOLEAN)
- screenshot_url (VARCHAR(500))
- created_at (TIMESTAMP)
```

### 1.2 Backend API Structure

#### Authentication Endpoints
- `POST /api/auth/platform-admin/login` - Platform admin login
- `POST /api/auth/tenant/login` - Tenant admin login
- `POST /api/auth/refresh` - Token refresh

#### Platform Admin Endpoints
- `GET /api/platform-admin/tenants` - List all tenants
- `POST /api/platform-admin/tenants` - Create new tenant
- `GET /api/platform-admin/tenants/{tenant_id}` - Get tenant details
- `PUT /api/platform-admin/tenants/{tenant_id}` - Update tenant
- `DELETE /api/platform-admin/tenants/{tenant_id}` - Deactivate tenant

#### Tenant Admin Endpoints (Client Admin)
- `GET /api/tenant/companies` - List companies for tenant
- `POST /api/tenant/companies` - Create new company
- `GET /api/tenant/companies/{company_id}/branches` - List branches
- `POST /api/tenant/companies/{company_id}/branches` - Create new branch
- `GET /api/tenant/users` - List users
- `POST /api/tenant/users` - Create new user
- `GET /api/tenant/agents` - List all agents (across companies/branches)
- `GET /api/tenant/download-agent/{org_id}` - Download agent for specific org_id

#### Agent Endpoints
- `POST /api/v1/agent/register` - Register new agent
- `POST /api/v1/agent/heartbeat` - Agent heartbeat
- `POST /api/v1/agent/telemetry` - Submit telemetry data

---

## Phase 2: Platform Admin Dashboard (Superadmin)

### 2.1 Authentication & Session Management
- Login page for platform admin
- JWT token-based authentication
- Session management middleware

### 2.2 Tenant Creation Workflow (Based on Flowchart)

#### Step 1: Add New Tenant
- Button/action to initiate tenant creation
- Modal or dedicated page for tenant creation

#### Step 2: Enter Tenant Details
- Form fields:
  - Tenant Name
  - Admin Email (for tenant admin login)
  - Admin Password
  - Contact Information
- **Auto-generate Tenant Org ID** (5-8 characters, unique)
  - Format: Alphanumeric (e.g., "TNT001", "ACME123")
  - Validation: Ensure uniqueness

#### Step 3: Enter Client Details
- Additional client-specific information:
  - Company Name (if different from tenant name)
  - Address
  - Phone Number
  - Industry Type

#### Step 4: Go to Client 360
- After tenant creation, redirect to Client 360 view
- This is a comprehensive tenant management dashboard

#### Step 5: Display Screens
- **Office Setup**: Manage companies and branches
- **Users**: Manage tenant users
- **Agents/EXE**: View and manage agents, download links

### 2.3 Client 360 Dashboard Features
- Tenant overview card
- Quick stats (companies, branches, agents, users)
- Navigation to:
  - Office Setup (Companies & Branches)
  - Users Management
  - Agents/EXE Management

---

## Phase 3: Tenant Admin Dashboard (Client Admin)

### 3.1 Authentication
- Login page using tenant credentials
- Tenant-specific session management

### 3.2 Company Management
- List all companies under the tenant
- Create new company
  - Company Name
  - **Auto-generate Company Org ID** (5-8 characters, unique)
- Edit/Delete companies

### 3.3 Branch Management
- List branches under a company
- Create new branch
  - Branch Name
  - Location
  - IP Addresses (multiple)
  - **Auto-generate Branch Org ID** (5-8 characters, unique)
- Edit/Delete branches

### 3.4 User Management
- List all users
- Create new user
  - Username
  - Email
  - Password
  - Role (Admin, Manager, Viewer)
- Edit/Delete users

### 3.5 Agent Download Feature
- Display list of all org_ids (tenant, companies, branches)
- For each org_id, provide download button
- Download endpoint: `GET /api/tenant/download-agent/{org_id}`
- Downloads MSI file named: `PrismTrack_Agent_{org_id}.msi`

---

## Phase 4: Agent Download & Dynamic MSI Generation

### 4.1 Master MSI Template
- Create a universal MSI installer using WiX Toolset
- The MSI should accept an `ORG_ID` parameter during installation
- Install Rust agent as Windows Service

### 4.2 Dynamic Download Endpoint
```python
@router.get("/api/tenant/download-agent/{org_id}")
async def download_agent(org_id: str, current_user: TenantUser):
    # Verify org_id belongs to tenant
    # Fetch master MSI template
    # Rename to PrismTrack_Agent_{org_id}.msi
    # Stream file to client
```

### 4.3 MSI Customization Logic
- Read master MSI file
- Embed org_id into MSI properties
- Rename output file
- Stream to client

---

## Phase 5: Rust Agent Development

### 5.1 Agent Bootstrapping
- On first run, extract org_id from:
  - Installation path
  - MSI property
  - Configuration file
- Register with backend: `POST /api/v1/agent/register`
- Receive and store agent_token
- Store org_id and agent_token in local config

### 5.2 Monitoring Capabilities
- **Window Tracking**: Log foreground window title and process name
- **Idle Detection**: Monitor keyboard/mouse activity
- **Screenshot Capture**: Take screenshots at randomized intervals
- **Activity Logging**: Track user activity patterns

### 5.3 Data Transmission
- Periodic heartbeat: `POST /api/v1/agent/heartbeat`
- Telemetry submission: `POST /api/v1/agent/telemetry`
- Offline queue: Store data locally if connection fails
- Sync when connection restored

### 5.4 Security Features
- Encrypt screenshots before upload
- Use agent_token for authentication
- Low CPU priority (stealth mode)
- No tray icon

---

## Phase 6: Frontend Implementation

### 6.1 Platform Admin UI
- **Login Page**: Simple form with username/password
- **Dashboard**: Overview of all tenants
- **Tenant Creation Flow**: Multi-step form matching flowchart
- **Client 360 View**: Comprehensive tenant management

### 6.2 Tenant Admin UI
- **Login Page**: Tenant-specific login
- **Dashboard**: Overview of companies, branches, agents
- **Company Management**: CRUD operations
- **Branch Management**: CRUD operations
- **User Management**: CRUD operations
- **Agent Download**: List with download buttons

### 6.3 UI Framework
- Use Tailwind CSS for styling
- Responsive design
- Simple, clean interface
- No complex frameworks (vanilla HTML/JS or minimal JS)

---

## Phase 7: Security & Authentication

### 7.1 Password Hashing
- Use bcrypt for password hashing
- Salt rounds: 12

### 7.2 JWT Tokens
- Access tokens (short-lived: 15 minutes)
- Refresh tokens (long-lived: 7 days)
- Token validation middleware

### 7.3 API Security
- Agent endpoints require agent_token
- Tenant endpoints require tenant JWT
- Platform admin endpoints require platform admin JWT
- CORS configuration
- Rate limiting

### 7.4 Org ID Generation Algorithm
```python
def generate_org_id(prefix: str = "") -> str:
    """
    Generate unique 5-8 character alphanumeric Org ID
    Format: [PREFIX][RANDOM]
    Examples: TNT001, ACME123, BR001
    """
    import random
    import string
    
    length = random.randint(5, 8)
    chars = string.ascii_uppercase + string.digits
    
    while True:
        org_id = prefix + ''.join(random.choices(chars, k=length-len(prefix)))
        if is_unique(org_id):
            return org_id
```

---

## Phase 8: Testing & Validation

### 8.1 Unit Tests
- Database models
- API endpoints
- Org ID generation
- Authentication logic

### 8.2 Integration Tests
- Tenant creation workflow
- Agent registration
- Telemetry submission
- Download flow

### 8.3 End-to-End Tests
- Complete tenant creation flow
- Agent installation and registration
- Data collection and display

---

## Phase 9: Deployment Preparation

### 9.1 Environment Configuration
- Development environment
- Production environment variables
- Database connection strings
- API keys and secrets

### 9.2 Documentation
- API documentation (OpenAPI/Swagger)
- Agent installation guide
- Admin user guide
- Developer setup guide

### 9.3 Build Scripts
- Database migration scripts
- MSI build automation
- Deployment scripts

---

## Implementation Priority

### MVP (Minimum Viable Product)
1. ✅ Database schema
2. ✅ Platform admin authentication
3. ✅ Tenant creation with Org ID generation
4. ✅ Tenant admin authentication
5. ✅ Company and Branch creation with Org IDs
6. ✅ Agent download endpoint (static MSI for now)
7. ✅ Basic Rust agent (registration and heartbeat)

### Phase 2 (Core Features)
1. ✅ User management
2. ✅ Agent telemetry collection
3. ✅ Dashboard views
4. ✅ Dynamic MSI generation

### Phase 3 (Advanced Features)
1. ✅ Screenshot capture and upload
2. ✅ Activity monitoring
3. ✅ Offline queue and sync
4. ✅ Advanced security features

---

## Key Implementation Notes

1. **Org ID Uniqueness**: Ensure all org_ids (tenant, company, branch) are globally unique
2. **Multi-level Hierarchy**: Support tenant → company → branch relationships
3. **Agent Association**: Agents can be associated with tenant, company, or branch org_id
4. **Download Security**: Verify tenant has access to org_id before allowing download
5. **Scalability**: Design for multiple tenants with many companies/branches
6. **Data Isolation**: Ensure tenant data is properly isolated

---

## Next Steps

1. Set up project structure
2. Initialize database schema
3. Create FastAPI application skeleton
4. Implement authentication system
5. Build Platform Admin dashboard
6. Build Tenant Admin dashboard
7. Develop Rust agent
8. Create MSI installer
9. Test end-to-end flow
10. Deploy prototype

