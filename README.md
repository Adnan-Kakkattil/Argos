# PrismTrack - Employee Tracking System

Multi-tenant enterprise employee monitoring system.

## Project Structure

```
Argos/
├── backend/                 # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Core configuration
│   ├── models/             # Database models
│   └── main.py             # FastAPI application
├── database/               # Database scripts
│   └── schema.sql          # MySQL schema
├── agent/                  # Rust agent (to be created)
├── installer/              # MSI installer (to be created)
├── frontend/               # HTML frontend (to be created)
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Setup Instructions

### 1. Database Setup

1. Install MySQL
2. Create database:
```bash
mysql -u root -p < database/schema.sql
```

Or manually:
```sql
CREATE DATABASE prismtrack;
USE prismtrack;
SOURCE database/schema.sql;
```

### 2. Backend Setup

1. Create virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the application:
```bash
python -m backend.main
# Or
uvicorn backend.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Credentials

**Platform Admin:**
- Username: `admin`
- Email: `admin@prismtrack.com`
- Password: `admin123` (CHANGE IN PRODUCTION!)

## Development Status

- ✅ Phase 1: Database Schema & Backend Foundation (In Progress)
- ⏳ Phase 2: Authentication System
- ⏳ Phase 3: Platform Admin Dashboard
- ⏳ Phase 4: Tenant Admin Dashboard
- ⏳ Phase 5: Agent Download System
- ⏳ Phase 6: Rust Agent Development

## API Endpoints

Coming soon...

## License

Proprietary

