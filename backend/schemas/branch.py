"""
Branch Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class BranchBase(BaseModel):
    name: str
    location: Optional[str] = None
    ip_addresses: Optional[str] = None  # JSON string or comma-separated

class BranchCreate(BranchBase):
    pass  # branch_org_id will be auto-generated

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    ip_addresses: Optional[str] = None
    is_active: Optional[bool] = None

class BranchResponse(BranchBase):
    id: int
    company_id: int
    branch_org_id: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    branches: List[BranchResponse]
    total: int

