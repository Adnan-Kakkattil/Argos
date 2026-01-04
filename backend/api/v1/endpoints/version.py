"""
Version Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import hashlib
import shutil
from datetime import datetime, timezone

from backend.core.database import get_db
from backend.core.dependencies import get_current_platform_admin
from backend.models.platform_admin import PlatformAdmin
from backend.models.agent_version import AgentVersion
from backend.models.agent import Agent
from backend.schemas.agent_version import (
    AgentVersionCreate,
    AgentVersionUpdate,
    AgentVersionResponse,
    AgentVersionListResponse,
    AgentUpdateCheckResponse
)

router = APIRouter()

# Directory for storing version files
# Go up from endpoints/version.py -> endpoints -> v1 -> api -> backend -> project_root
# Then into backend/static/agents/versions
VERSIONS_DIR = Path(__file__).resolve().parents[3] / "static" / "agents" / "versions"
VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@router.get("/versions", response_model=AgentVersionListResponse, tags=["version"])
async def list_versions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    List all agent versions
    """
    versions = db.query(AgentVersion).order_by(AgentVersion.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(AgentVersion).count()
    
    return {
        "versions": versions,
        "total": total
    }

@router.get("/versions/{version_id}", response_model=AgentVersionResponse, tags=["version"])
async def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Get version details by ID
    """
    version = db.query(AgentVersion).filter(AgentVersion.id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    return version

@router.post("/versions", response_model=AgentVersionResponse, tags=["version"])
async def create_version(
    version_number: str = Form(...),
    changelog: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Create a new agent version
    
    Uploads a zip file containing the agent update.
    Only one version can be marked as latest at a time.
    """
    # Validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .zip files are allowed"
        )
    
    # Check if version number already exists
    existing = db.query(AgentVersion).filter(AgentVersion.version_number == version_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Version {version_number} already exists"
        )
    
    # Save uploaded file
    file_path = VERSIONS_DIR / f"agent_v{version_number}.zip"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Calculate file size and hash
        file_size = file_path.stat().st_size
        file_hash = calculate_file_hash(file_path)
        
        # If this is marked as latest, unmark other latest versions
        # (We'll set is_latest=True by default, but admin can change it)
        is_latest = True  # New version is latest by default
        
        if is_latest:
            # Unmark all other versions as latest
            db.query(AgentVersion).filter(AgentVersion.is_latest == True).update({"is_latest": False})
        
        # Create version record
        # Store relative path from static directory
        static_dir = Path(__file__).resolve().parents[3] / "static"
        relative_path = file_path.relative_to(static_dir)
        
        version = AgentVersion(
            version_number=version_number,
            changelog=changelog,
            file_path=str(relative_path),  # Relative path from static
            file_size=file_size,
            file_hash=file_hash,
            is_active=True,
            is_latest=is_latest,
            created_by=current_admin.id,
            released_at=datetime.now(timezone.utc)
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version
        
    except Exception as e:
        # Clean up file if database operation fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating version: {str(e)}"
        )

@router.put("/versions/{version_id}", response_model=AgentVersionResponse, tags=["version"])
async def update_version(
    version_id: int,
    version_data: AgentVersionUpdate,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Update version details
    """
    version = db.query(AgentVersion).filter(AgentVersion.id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Update fields
    if version_data.version_number is not None:
        # Check if new version number already exists
        existing = db.query(AgentVersion).filter(
            AgentVersion.version_number == version_data.version_number,
            AgentVersion.id != version_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version {version_data.version_number} already exists"
            )
        version.version_number = version_data.version_number
    
    if version_data.changelog is not None:
        version.changelog = version_data.changelog
    
    if version_data.is_active is not None:
        version.is_active = version_data.is_active
    
    if version_data.is_latest is not None:
        # If setting as latest, unmark other latest versions
        if version_data.is_latest:
            db.query(AgentVersion).filter(
                AgentVersion.is_latest == True,
                AgentVersion.id != version_id
            ).update({"is_latest": False})
        version.is_latest = version_data.is_latest
    
    if version_data.released_at is not None:
        version.released_at = version_data.released_at
    
    db.commit()
    db.refresh(version)
    
    return version

@router.delete("/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["version"])
async def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Delete a version (soft delete - sets is_active=False)
    """
    version = db.query(AgentVersion).filter(AgentVersion.id == version_id).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )
    
    # Soft delete
    version.is_active = False
    db.commit()
    
    return None

@router.get("/agent/check-update", response_model=AgentUpdateCheckResponse, tags=["agent"])
async def check_agent_update(
    current_version: Optional[str] = None,
    x_agent_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Check if agent update is available
    
    Agents call this endpoint periodically to check for updates.
    If update is available, returns download URL and metadata.
    """
    # Get latest active version
    latest_version = db.query(AgentVersion).filter(
        AgentVersion.is_active == True,
        AgentVersion.is_latest == True
    ).first()
    
    if not latest_version:
        return {
            "update_available": False,
            "current_version": current_version,
            "latest_version": None
        }
    
    # Compare versions (simple string comparison, can be enhanced with semver)
    update_available = current_version != latest_version.version_number
    
    # If agent token provided, update agent's current_version
    if x_agent_token and update_available:
        agent = db.query(Agent).filter(Agent.agent_token == x_agent_token).first()
        if agent:
            agent.current_version = current_version
            db.commit()
    
    if update_available:
        # Build download URL
        download_url = f"/static/agents/versions/agent_v{latest_version.version_number}.zip"
        
        return {
            "update_available": True,
            "current_version": current_version,
            "latest_version": latest_version.version_number,
            "changelog": latest_version.changelog,
            "download_url": download_url,
            "file_size": latest_version.file_size,
            "file_hash": latest_version.file_hash
        }
    else:
        return {
            "update_available": False,
            "current_version": current_version,
            "latest_version": latest_version.version_number
        }

@router.get("/agent/download-update/{version_number}", tags=["agent"])
async def download_agent_update(
    version_number: str,
    x_agent_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Download agent update zip file
    
    Agents use this endpoint to download the update file.
    """
    from fastapi.responses import FileResponse
    
    # Verify version exists and is active
    version = db.query(AgentVersion).filter(
        AgentVersion.version_number == version_number,
        AgentVersion.is_active == True
    ).first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found or inactive"
        )
    
    # Build file path
    file_path = Path(__file__).resolve().parents[3] / "static" / "agents" / "versions" / f"agent_v{version_number}.zip"
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version file not found on server"
        )
    
    # Update agent's current_version if token provided
    if x_agent_token:
        agent = db.query(Agent).filter(Agent.agent_token == x_agent_token).first()
        if agent:
            agent.current_version = version_number
            db.commit()
    
    filename = f"PrismTrackAgent_v{version_number}.zip"
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/zip",
        headers={
            "X-Version-Number": version_number,
            "X-File-Hash": version.file_hash or "",
            "X-File-Size": str(version.file_size)
        }
    )

