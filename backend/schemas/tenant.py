"""
Tenant Schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class TenantBase(BaseModel):
    name: str
    admin_email: EmailStr

class TenantCreate(TenantBase):
    admin_password: str
    # Optional client details (Step 3 of workflow)
    company_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    industry_type: Optional[str] = None
    # Note: These client details can be stored in a separate table later if needed
    # For now, we'll focus on core tenant creation

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    admin_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class TenantResponse(TenantBase):
    id: int
    tenant_org_id: str
    admin_api_key: str
    created_by: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class TenantListResponse(BaseModel):
    tenants: List[TenantResponse]
    total: int

