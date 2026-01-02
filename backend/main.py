"""
PrismTrack - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.core.config import settings
from backend.api.v1 import api_router

app = FastAPI(
    title="PrismTrack API",
    description="Multi-tenant Employee Tracking System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files directory for agent downloads
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
agents_dir = static_dir / "agents"
agents_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Get CORS origins from settings
cors_origins = settings.get_cors_origins()

# Add CORS middleware - MUST be added before routes
# FastAPI's CORSMiddleware automatically handles OPTIONS preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # List of allowed origins (not "*" when credentials=True)
    allow_credentials=True,  # Allow cookies/credentials
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to frontend
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "message": "PrismTrack API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

