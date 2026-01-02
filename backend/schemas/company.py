"""
Company Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CompanyBase(BaseModel):
    name: str

class CompanyCreate(CompanyBase):
    pass  # company_org_id will be auto-generated

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    id: int
    tenant_id: int
    company_org_id: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
    total: int

