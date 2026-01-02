"""
Platform Admin Schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class PlatformAdminBase(BaseModel):
    username: str
    email: EmailStr

class PlatformAdminCreate(PlatformAdminBase):
    password: str

class PlatformAdminResponse(PlatformAdminBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

