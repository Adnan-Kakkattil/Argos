"""
Authentication Schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PlatformAdminLogin(BaseModel):
    username: str
    password: str

class TenantLogin(BaseModel):
    email: EmailStr
    password: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

