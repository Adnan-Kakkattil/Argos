"""
Platform Admin Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.core.dependencies import get_current_platform_admin
from backend.core.security import hash_password, generate_api_key
from backend.core.utils import generate_org_id
from backend.models.platform_admin import PlatformAdmin
from backend.models.tenant import Tenant
from backend.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantListResponse

router = APIRouter()

@router.get("/tenants", response_model=TenantListResponse, tags=["platform-admin"])
async def list_tenants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    List all tenants
    
    Returns paginated list of all tenants in the system
    """
    tenants = db.query(Tenant).offset(skip).limit(limit).all()
    total = db.query(Tenant).count()
    
    return {
        "tenants": tenants,
        "total": total
    }

@router.get("/tenants/{tenant_id}", response_model=TenantResponse, tags=["platform-admin"])
async def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Get tenant details by ID
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant

@router.post("/tenants", response_model=TenantResponse, tags=["platform-admin"])
async def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Create a new tenant
    
    This endpoint implements the tenant creation workflow:
    1. Generate unique tenant_org_id (5-8 characters)
    2. Hash the admin password
    3. Generate admin_api_key
    4. Create tenant record
    """
    # Check if tenant with same email already exists
    existing_tenant = db.query(Tenant).filter(
        Tenant.admin_email == tenant_data.admin_email
    ).first()
    
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant with this email already exists"
        )
    
    # Generate unique tenant_org_id
    tenant_org_id = generate_org_id(prefix="", length=None, db=db)
    
    # Hash the admin password
    admin_password_hash = hash_password(tenant_data.admin_password)
    
    # Generate admin API key
    admin_api_key = generate_api_key()
    
    # Create tenant
    tenant = Tenant(
        tenant_org_id=tenant_org_id,
        name=tenant_data.name,
        admin_email=tenant_data.admin_email,
        admin_password_hash=admin_password_hash,
        admin_api_key=admin_api_key,
        created_by=current_admin.id,
        is_active=True
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return tenant

@router.put("/tenants/{tenant_id}", response_model=TenantResponse, tags=["platform-admin"])
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Update tenant details
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Update fields if provided
    if tenant_data.name is not None:
        tenant.name = tenant_data.name
    if tenant_data.admin_email is not None:
        # Check if email is already taken by another tenant
        existing = db.query(Tenant).filter(
            Tenant.admin_email == tenant_data.admin_email,
            Tenant.id != tenant_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another tenant"
            )
        tenant.admin_email = tenant_data.admin_email
    if tenant_data.is_active is not None:
        tenant.is_active = tenant_data.is_active
    
    db.commit()
    db.refresh(tenant)
    
    return tenant

@router.delete("/tenants/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["platform-admin"])
async def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Deactivate a tenant (soft delete)
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Soft delete - set is_active to False
    tenant.is_active = False
    db.commit()
    
    return None

@router.get("/tenants/{tenant_id}/stats", tags=["platform-admin"])
async def get_tenant_stats(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_admin: PlatformAdmin = Depends(get_current_platform_admin)
):
    """
    Get tenant statistics for Client 360 view
    
    Returns:
    - Tenant details
    - Number of companies
    - Number of branches
    - Number of users
    - Number of agents
    """
    from backend.models.company import Company
    from backend.models.branch import Branch
    from backend.models.user import User
    from backend.models.agent import Agent
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Count companies
    companies_count = db.query(Company).filter(
        Company.tenant_id == tenant_id,
        Company.is_active == True
    ).count()
    
    # Count branches (through companies)
    branches_count = db.query(Branch).join(Company).filter(
        Company.tenant_id == tenant_id,
        Branch.is_active == True
    ).count()
    
    # Count users
    users_count = db.query(User).filter(
        User.tenant_id == tenant_id,
        User.is_active == True
    ).count()
    
    # Count agents (by org_id matching tenant_org_id)
    agents_count = db.query(Agent).filter(
        Agent.org_id == tenant.tenant_org_id
    ).count()
    
    return {
        "tenant": {
            "id": tenant.id,
            "tenant_org_id": tenant.tenant_org_id,
            "name": tenant.name,
            "admin_email": tenant.admin_email,
            "created_at": tenant.created_at,
            "is_active": tenant.is_active
        },
        "statistics": {
            "companies": companies_count,
            "branches": branches_count,
            "users": users_count,
            "agents": agents_count
        }
    }

