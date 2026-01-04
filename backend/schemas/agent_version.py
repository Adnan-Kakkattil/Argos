"""
Agent Version Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AgentVersionBase(BaseModel):
    version_number: str
    changelog: str

class AgentVersionCreate(AgentVersionBase):
    pass  # File upload handled separately

class AgentVersionUpdate(BaseModel):
    version_number: Optional[str] = None
    changelog: Optional[str] = None
    is_active: Optional[bool] = None
    is_latest: Optional[bool] = None
    released_at: Optional[datetime] = None

class AgentVersionResponse(AgentVersionBase):
    id: int
    file_path: str
    file_size: int
    file_hash: Optional[str]
    is_active: bool
    is_latest: bool
    created_by: Optional[int]
    created_at: datetime
    released_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AgentVersionListResponse(BaseModel):
    versions: List[AgentVersionResponse]
    total: int

class AgentUpdateCheckResponse(BaseModel):
    update_available: bool
    latest_version: Optional[str] = None
    current_version: Optional[str] = None
    changelog: Optional[str] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None

