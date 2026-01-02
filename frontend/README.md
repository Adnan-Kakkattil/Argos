# PrismTrack Frontend

Basic HTML/JavaScript UI for PrismTrack Employee Tracking System.

## Features

### Platform Admin
- Login page
- Dashboard with tenant list
- Create tenant workflow
- Client 360 view with statistics

### Tenant Admin
- Login page
- Dashboard with companies, users, and agent downloads
- Create company
- Create user
- View branches
- Download agents for different org_ids

## Setup

1. Make sure the backend API is running on `http://localhost:8000`
2. Open `index.html` in a browser or serve it with a web server

## Running

### Option 1: Simple HTTP Server (Python)
```bash
cd frontend
python -m http.server 8080
```
Then open: http://localhost:8080

### Option 2: Direct File
Open `index.html` directly in your browser (may have CORS issues with API calls)

### Option 3: Live Server (VS Code)
Use the Live Server extension in VS Code

## API Configuration

The API base URL is configured in `js/api.js`:
```javascript
const API_BASE = 'http://localhost:8000/api/v1';
```

Change this if your backend is running on a different host/port.

## Default Credentials

### Platform Admin
- Username: `admin`
- Password: `admin123`

### Tenant Admin
- Use credentials created when creating a tenant via Platform Admin

## Features Implemented

✅ Platform Admin Login
✅ Tenant Creation Workflow
✅ Client 360 Dashboard
✅ Tenant Admin Login
✅ Company Management
✅ User Management
✅ Agent Download Interface
✅ Responsive Design with Tailwind CSS

## Notes

- Uses Tailwind CSS CDN for styling
- No build process required
- Pure JavaScript (no frameworks)
- Token-based authentication
- Automatic token refresh

