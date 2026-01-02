# PrismTrack Development Checklist

## Project Setup & Configuration

### Environment Setup
- [ ] Create project directory structure
- [ ] Set up Python virtual environment
- [ ] Install FastAPI and dependencies (fastapi, uvicorn, sqlalchemy, pymysql, pydantic, bcrypt, python-jose, python-multipart)
- [ ] Set up MySQL database
- [ ] Create `.env` file for environment variables
- [ ] Set up Rust development environment
- [ ] Install WiX Toolset for MSI creation

### Project Structure
- [ ] Create backend directory (`backend/`)
- [ ] Create frontend directory (`frontend/`)
- [ ] Create agent directory (`agent/`)
- [ ] Create installer directory (`installer/`)
- [ ] Create database migrations directory
- [ ] Create configuration files (requirements.txt, Cargo.toml, etc.)

---

## Phase 1: Database & Backend Foundation

### Database Schema
- [ ] Create `platform_admins` table
- [ ] Create `tenants` table with `tenant_org_id` field
- [ ] Create `companies` table with `company_org_id` field
- [ ] Create `branches` table with `branch_org_id` field
- [ ] Create `users` table
- [ ] Create `agents` table
- [ ] Create `telemetry` table
- [ ] Add foreign key constraints
- [ ] Add indexes for performance (org_ids, foreign keys)
- [ ] Create database migration scripts

### Backend Core
- [ ] Initialize FastAPI application
- [ ] Set up database connection (SQLAlchemy)
- [ ] Create database models (SQLAlchemy ORM)
- [ ] Create Pydantic schemas for request/response
- [ ] Set up CORS middleware
- [ ] Configure logging

### Org ID Generation
- [ ] Implement `generate_org_id()` function
- [ ] Add uniqueness validation
- [ ] Test org ID generation (5-8 characters)
- [ ] Ensure global uniqueness across all org types

---

## Phase 2: Authentication System

### Platform Admin Authentication
- [ ] Create platform admin login endpoint (`POST /api/auth/platform-admin/login`)
- [ ] Implement password hashing (bcrypt)
- [ ] Generate JWT tokens (access + refresh)
- [ ] Create JWT token validation middleware
- [ ] Create platform admin seed script (initial superadmin)

### Tenant Authentication
- [ ] Create tenant login endpoint (`POST /api/auth/tenant/login`)
- [ ] Implement tenant JWT token generation
- [ ] Create tenant authentication middleware
- [ ] Test authentication flow

### Security
- [ ] Implement password strength validation
- [ ] Add rate limiting to login endpoints
- [ ] Configure token expiration times
- [ ] Implement token refresh endpoint

---

## Phase 3: Platform Admin Dashboard

### Platform Admin UI - Login
- [ ] Create login page HTML
- [ ] Style with Tailwind CSS
- [ ] Add form validation
- [ ] Implement login API call
- [ ] Handle authentication errors
- [ ] Store JWT token in localStorage/sessionStorage

### Platform Admin UI - Dashboard
- [ ] Create dashboard layout
- [ ] Display list of tenants
- [ ] Add navigation menu
- [ ] Show tenant statistics
- [ ] Implement logout functionality

### Tenant Creation Workflow
- [ ] **Step 1**: Create "Add New Tenant" button/page
- [ ] **Step 2**: Create tenant details form
  - [ ] Tenant name field
  - [ ] Admin email field
  - [ ] Admin password field
  - [ ] Contact information fields
  - [ ] Auto-generate tenant_org_id (display to user)
- [ ] **Step 3**: Create client details form
  - [ ] Company name field
  - [ ] Address field
  - [ ] Phone number field
  - [ ] Industry type field
- [ ] **Step 4**: Create Client 360 view
  - [ ] Tenant overview card
  - [ ] Quick statistics
  - [ ] Navigation links
- [ ] **Step 5**: Create navigation to:
  - [ ] Office Setup (Companies & Branches)
  - [ ] Users Management
  - [ ] Agents/EXE Management

### Platform Admin API Endpoints
- [ ] `GET /api/platform-admin/tenants` - List tenants
- [ ] `POST /api/platform-admin/tenants` - Create tenant
- [ ] `GET /api/platform-admin/tenants/{id}` - Get tenant details
- [ ] `PUT /api/platform-admin/tenants/{id}` - Update tenant
- [ ] `DELETE /api/platform-admin/tenants/{id}` - Deactivate tenant
- [ ] Test all endpoints

---

## Phase 4: Tenant Admin Dashboard (Client Admin)

### Tenant Admin UI - Login
- [ ] Create tenant login page
- [ ] Style with Tailwind CSS
- [ ] Implement tenant authentication
- [ ] Redirect to tenant dashboard on success

### Tenant Admin UI - Dashboard
- [ ] Create tenant dashboard layout
- [ ] Display overview statistics
- [ ] Show companies, branches, agents count
- [ ] Add navigation menu

### Company Management
- [ ] Create companies list page
- [ ] Create "Add New Company" form
  - [ ] Company name field
  - [ ] Auto-generate company_org_id
- [ ] Implement edit company functionality
- [ ] Implement delete company functionality
- [ ] Test company CRUD operations

### Branch Management
- [ ] Create branches list page (under company)
- [ ] Create "Add New Branch" form
  - [ ] Branch name field
  - [ ] Location field
  - [ ] IP addresses field (multiple)
  - [ ] Auto-generate branch_org_id
- [ ] Implement edit branch functionality
- [ ] Implement delete branch functionality
- [ ] Test branch CRUD operations

### User Management
- [ ] Create users list page
- [ ] Create "Add New User" form
  - [ ] Username field
  - [ ] Email field
  - [ ] Password field
  - [ ] Role selection (Admin, Manager, Viewer)
- [ ] Implement edit user functionality
- [ ] Implement delete user functionality
- [ ] Test user CRUD operations

### Agent Download Feature
- [ ] Create agent download page
- [ ] List all org_ids (tenant, companies, branches)
- [ ] Add download button for each org_id
- [ ] Implement download functionality
- [ ] Test download flow

### Tenant Admin API Endpoints
- [ ] `GET /api/tenant/companies` - List companies
- [ ] `POST /api/tenant/companies` - Create company
- [ ] `GET /api/tenant/companies/{id}/branches` - List branches
- [ ] `POST /api/tenant/companies/{id}/branches` - Create branch
- [ ] `GET /api/tenant/users` - List users
- [ ] `POST /api/tenant/users` - Create user
- [ ] `GET /api/tenant/agents` - List agents
- [ ] `GET /api/tenant/download-agent/{org_id}` - Download agent
- [ ] Test all endpoints

---

## Phase 5: Agent Download System

### MSI Template
- [ ] Create master MSI template using WiX Toolset
- [ ] Configure MSI to accept ORG_ID parameter
- [ ] Set up Windows Service installation
- [ ] Test MSI installation manually

### Dynamic Download Endpoint
- [ ] Implement `GET /api/tenant/download-agent/{org_id}` endpoint
- [ ] Verify tenant has access to org_id
- [ ] Read master MSI file
- [ ] Embed org_id into MSI
- [ ] Rename file to `PrismTrack_Agent_{org_id}.msi`
- [ ] Stream file to client
- [ ] Test download functionality

### MSI Customization
- [ ] Research MSI property injection methods
- [ ] Implement org_id embedding logic
- [ ] Test MSI with different org_ids
- [ ] Verify org_id is accessible to agent after installation

---

## Phase 6: Rust Agent Development

### Agent Project Setup
- [ ] Initialize Rust project
- [ ] Add dependencies (tokio, reqwest, serde, winapi, etc.)
- [ ] Create project structure
- [ ] Set up configuration management

### Agent Bootstrapping
- [ ] Implement org_id extraction from:
  - [ ] Installation path
  - [ ] MSI property
  - [ ] Configuration file
- [ ] Create agent registration function
- [ ] Implement `POST /api/v1/agent/register` call
- [ ] Store agent_token locally
- [ ] Create local configuration file

### Monitoring Features
- [ ] Implement window tracking (foreground window)
- [ ] Implement idle detection (keyboard/mouse)
- [ ] Implement screenshot capture
- [ ] Set up monitoring loop (10-30 second intervals)
- [ ] Test monitoring functionality

### Data Transmission
- [ ] Implement heartbeat endpoint (`POST /api/v1/agent/heartbeat`)
- [ ] Implement telemetry submission (`POST /api/v1/agent/telemetry`)
- [ ] Create offline queue (SQLite)
- [ ] Implement sync when connection restored
- [ ] Test data transmission

### Security & Stealth
- [ ] Implement screenshot encryption
- [ ] Use agent_token for API authentication
- [ ] Set low CPU priority
- [ ] Remove tray icon
- [ ] Test stealth mode

### Windows Service
- [ ] Configure agent as Windows Service
- [ ] Implement service start/stop logic
- [ ] Test service installation
- [ ] Test auto-start on boot

---

## Phase 7: Agent API Endpoints

### Backend Agent Endpoints
- [ ] `POST /api/v1/agent/register` - Register new agent
  - [ ] Validate org_id
  - [ ] Generate agent_token
  - [ ] Store agent in database
  - [ ] Return agent_token
- [ ] `POST /api/v1/agent/heartbeat` - Agent heartbeat
  - [ ] Validate agent_token
  - [ ] Update last_seen timestamp
  - [ ] Update agent status
- [ ] `POST /api/v1/agent/telemetry` - Submit telemetry
  - [ ] Validate agent_token
  - [ ] Store telemetry data
  - [ ] Handle screenshot uploads
- [ ] Test all agent endpoints

---

## Phase 8: Frontend Polish & UX

### UI/UX Improvements
- [ ] Add loading states
- [ ] Add error handling and display
- [ ] Add success notifications
- [ ] Improve form validation
- [ ] Add responsive design
- [ ] Test on different screen sizes

### Dashboard Enhancements
- [ ] Add charts/graphs for statistics
- [ ] Implement real-time updates (WebSocket or polling)
- [ ] Add search and filtering
- [ ] Add pagination for large lists

---

## Phase 9: Testing

### Unit Tests
- [ ] Test database models
- [ ] Test API endpoints
- [ ] Test org_id generation
- [ ] Test authentication logic
- [ ] Test password hashing

### Integration Tests
- [ ] Test tenant creation workflow
- [ ] Test company/branch creation
- [ ] Test agent registration
- [ ] Test telemetry submission
- [ ] Test download flow

### End-to-End Tests
- [ ] Test complete tenant creation flow
- [ ] Test tenant login and dashboard access
- [ ] Test agent download and installation
- [ ] Test agent registration and data collection
- [ ] Test data display in dashboard

### Manual Testing
- [ ] Test platform admin login
- [ ] Test tenant creation (all steps)
- [ ] Test tenant admin login
- [ ] Test company/branch creation
- [ ] Test agent download
- [ ] Test agent installation
- [ ] Test agent registration
- [ ] Test telemetry collection
- [ ] Test data display

---

## Phase 10: Documentation & Deployment

### Documentation
- [ ] Write API documentation (OpenAPI/Swagger)
- [ ] Create agent installation guide
- [ ] Create admin user guide
- [ ] Create developer setup guide
- [ ] Document database schema
- [ ] Document environment variables

### Deployment Preparation
- [ ] Create production environment configuration
- [ ] Set up database backup scripts
- [ ] Create deployment scripts
- [ ] Set up logging and monitoring
- [ ] Configure error tracking

### Build & Release
- [ ] Create build scripts for backend
- [ ] Create build scripts for agent
- [ ] Create MSI build automation
- [ ] Test complete build process
- [ ] Create release package

---

## Phase 11: Security Audit

### Security Checklist
- [ ] Review password hashing implementation
- [ ] Review JWT token security
- [ ] Review API endpoint security
- [ ] Review agent authentication
- [ ] Review data encryption
- [ ] Review SQL injection prevention
- [ ] Review XSS prevention
- [ ] Review CORS configuration
- [ ] Review rate limiting
- [ ] Perform security testing

---

## Phase 12: Performance Optimization

### Performance Tasks
- [ ] Optimize database queries
- [ ] Add database indexes
- [ ] Implement caching where appropriate
- [ ] Optimize API response times
- [ ] Optimize agent resource usage
- [ ] Test under load

---

## Final Checklist

### Pre-Launch
- [ ] All critical features implemented
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Performance acceptable
- [ ] Deployment scripts ready
- [ ] Backup strategy in place

### Launch
- [ ] Deploy to production
- [ ] Verify all services running
- [ ] Test production environment
- [ ] Monitor for issues
- [ ] Gather user feedback

---

## Notes

- **Org ID Format**: Ensure all org_ids are 5-8 characters, alphanumeric, globally unique
- **Multi-level Hierarchy**: Tenant → Company → Branch relationships must be maintained
- **Agent Association**: Agents can be associated with any org_id (tenant, company, or branch)
- **Download Security**: Always verify tenant access before allowing agent download
- **Data Isolation**: Ensure proper tenant data isolation in all queries

---

## Progress Tracking

**Current Status**: Not Started
**Last Updated**: [Date]
**Next Milestone**: [Milestone Name]

