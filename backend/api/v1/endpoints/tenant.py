"""
Tenant Admin (Client Admin) Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant
from backend.core.security import hash_password
from backend.core.utils import generate_org_id
from backend.models.tenant import Tenant
from backend.models.company import Company
from backend.models.branch import Branch
from backend.models.user import User
from backend.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from backend.schemas.branch import BranchCreate, BranchUpdate, BranchResponse, BranchListResponse
from backend.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from backend.schemas.agent import AgentResponse, AgentListResponse, TelemetryListResponse

router = APIRouter()

# ==================== Company Management ====================

@router.get("/companies", response_model=CompanyListResponse, tags=["tenant"])
async def list_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all companies for the current tenant
    """
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).offset(skip).limit(limit).all()
    
    total = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).count()
    
    return {
        "companies": companies,
        "total": total
    }

@router.get("/companies/{company_id}", response_model=CompanyResponse, tags=["tenant"])
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get company details
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.post("/companies", response_model=CompanyResponse, tags=["tenant"])
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create a new company
    
    Auto-generates company_org_id (5-8 characters, globally unique)
    """
    # Generate unique company_org_id
    company_org_id = generate_org_id(prefix="", length=None, db=db)
    
    # Create company
    company = Company(
        tenant_id=current_tenant.id,
        company_org_id=company_org_id,
        name=company_data.name,
        is_active=True
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company

@router.put("/companies/{company_id}", response_model=CompanyResponse, tags=["tenant"])
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update company details
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if company_data.name is not None:
        company.name = company_data.name
    if company_data.is_active is not None:
        company.is_active = company_data.is_active
    
    db.commit()
    db.refresh(company)
    
    return company

@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tenant"])
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Deactivate a company (soft delete)
    """
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    company.is_active = False
    db.commit()
    
    return None

# ==================== Branch Management ====================

@router.get("/companies/{company_id}/branches", response_model=BranchListResponse, tags=["tenant"])
async def list_branches(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all branches for a company
    """
    # Verify company belongs to tenant
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    branches = db.query(Branch).filter(
        Branch.company_id == company_id,
        Branch.is_active == True
    ).offset(skip).limit(limit).all()
    
    total = db.query(Branch).filter(
        Branch.company_id == company_id,
        Branch.is_active == True
    ).count()
    
    return {
        "branches": branches,
        "total": total
    }

@router.get("/branches/{branch_id}", response_model=BranchResponse, tags=["tenant"])
async def get_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get branch details
    """
    branch = db.query(Branch).join(Company).filter(
        Branch.id == branch_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    return branch

@router.post("/companies/{company_id}/branches", response_model=BranchResponse, tags=["tenant"])
async def create_branch(
    company_id: int,
    branch_data: BranchCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create a new branch
    
    Auto-generates branch_org_id (5-8 characters, globally unique)
    """
    # Verify company belongs to tenant
    company = db.query(Company).filter(
        Company.id == company_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Generate unique branch_org_id
    branch_org_id = generate_org_id(prefix="", length=None, db=db)
    
    # Create branch
    branch = Branch(
        company_id=company_id,
        branch_org_id=branch_org_id,
        name=branch_data.name,
        location=branch_data.location,
        ip_addresses=branch_data.ip_addresses,
        is_active=True
    )
    
    db.add(branch)
    db.commit()
    db.refresh(branch)
    
    return branch

@router.put("/branches/{branch_id}", response_model=BranchResponse, tags=["tenant"])
async def update_branch(
    branch_id: int,
    branch_data: BranchUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update branch details
    """
    branch = db.query(Branch).join(Company).filter(
        Branch.id == branch_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    if branch_data.name is not None:
        branch.name = branch_data.name
    if branch_data.location is not None:
        branch.location = branch_data.location
    if branch_data.ip_addresses is not None:
        branch.ip_addresses = branch_data.ip_addresses
    if branch_data.is_active is not None:
        branch.is_active = branch_data.is_active
    
    db.commit()
    db.refresh(branch)
    
    return branch

@router.delete("/branches/{branch_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tenant"])
async def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Deactivate a branch (soft delete)
    """
    branch = db.query(Branch).join(Company).filter(
        Branch.id == branch_id,
        Company.tenant_id == current_tenant.id
    ).first()
    
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch not found"
        )
    
    branch.is_active = False
    db.commit()
    
    return None

# ==================== User Management ====================

@router.get("/users", response_model=UserListResponse, tags=["tenant"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all users for the current tenant
    """
    users = db.query(User).filter(
        User.tenant_id == current_tenant.id,
        User.is_active == True
    ).offset(skip).limit(limit).all()
    
    total = db.query(User).filter(
        User.tenant_id == current_tenant.id,
        User.is_active == True
    ).count()
    
    return {
        "users": users,
        "total": total
    }

@router.get("/users/{user_id}", response_model=UserResponse, tags=["tenant"])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get user details
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/users", response_model=UserResponse, tags=["tenant"])
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Create a new user (client admin user)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    user = User(
        tenant_id=current_tenant.id,
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        role=user_data.role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse, tags=["tenant"])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Update user details
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        # Check if email is already taken by another user
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another user"
            )
        user.email = user_data.email
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tenant"])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Deactivate a user (soft delete)
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    return None

# ==================== Agent Management ====================

@router.get("/agents", response_model=AgentListResponse, tags=["tenant"])
async def list_tenant_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all agents for the current tenant
    
    Returns agents for tenant org_id, all company org_ids, and all branch org_ids.
    """
    from backend.models.agent import Agent
    
    # Get all org_ids for this tenant
    tenant_org_id = current_tenant.tenant_org_id
    
    # Get company org_ids
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).all()
    company_org_ids = [c.company_org_id for c in companies]
    
    # Get branch org_ids
    branches = db.query(Branch).join(Company).filter(
        Company.tenant_id == current_tenant.id,
        Branch.is_active == True
    ).all()
    branch_org_ids = [b.branch_org_id for b in branches]
    
    # Get all agents matching any of these org_ids
    all_org_ids = [tenant_org_id] + company_org_ids + branch_org_ids
    
    query = db.query(Agent).filter(Agent.org_id.in_(all_org_ids))
    
    agents = query.order_by(Agent.last_seen.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "agents": agents,
        "total": total
    }

@router.get("/agents/{agent_id}", response_model=AgentResponse, tags=["tenant"])
async def get_tenant_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get agent details for a specific agent (must belong to tenant)
    """
    from backend.models.agent import Agent
    
    # Get agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Verify agent belongs to tenant
    tenant_org_id = current_tenant.tenant_org_id
    
    # Get company org_ids
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).all()
    company_org_ids = [c.company_org_id for c in companies]
    
    # Get branch org_ids
    branches = db.query(Branch).join(Company).filter(
        Company.tenant_id == current_tenant.id,
        Branch.is_active == True
    ).all()
    branch_org_ids = [b.branch_org_id for b in branches]
    
    all_org_ids = [tenant_org_id] + company_org_ids + branch_org_ids
    
    if agent.org_id not in all_org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to this tenant"
        )
    
    return agent

@router.get("/agents/{agent_id}/telemetry", response_model=TelemetryListResponse, tags=["tenant"])
async def get_agent_telemetry(
    agent_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Get telemetry data for a specific agent
    
    Returns recent telemetry records ordered by timestamp (newest first).
    """
    from backend.models.agent import Agent
    from backend.models.telemetry import Telemetry
    
    # Get and verify agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Verify agent belongs to tenant
    tenant_org_id = current_tenant.tenant_org_id
    
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).all()
    company_org_ids = [c.company_org_id for c in companies]
    
    branches = db.query(Branch).join(Company).filter(
        Company.tenant_id == current_tenant.id,
        Branch.is_active == True
    ).all()
    branch_org_ids = [b.branch_org_id for b in branches]
    
    all_org_ids = [tenant_org_id] + company_org_ids + branch_org_ids
    
    if agent.org_id not in all_org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to this tenant"
        )
    
    # Get telemetry data
    telemetry = db.query(Telemetry).filter(
        Telemetry.agent_id == agent_id
    ).order_by(Telemetry.timestamp.desc()).offset(skip).limit(limit).all()
    
    total = db.query(Telemetry).filter(Telemetry.agent_id == agent_id).count()
    
    return {
        "agent_id": agent_id,
        "telemetry": telemetry,
        "total": total
    }

# ==================== Agent Download ====================

@router.get("/org-ids", tags=["tenant"])
async def list_org_ids(
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    List all org_ids available for agent download
    
    Returns:
    - Tenant org_id
    - All company org_ids
    - All branch org_ids
    """
    # Get tenant org_id
    tenant_org = {
        "org_id": current_tenant.tenant_org_id,
        "type": "tenant",
        "name": current_tenant.name,
        "id": current_tenant.id
    }
    
    # Get all company org_ids
    companies = db.query(Company).filter(
        Company.tenant_id == current_tenant.id,
        Company.is_active == True
    ).all()
    
    company_orgs = [
        {
            "org_id": company.company_org_id,
            "type": "company",
            "name": company.name,
            "id": company.id
        }
        for company in companies
    ]
    
    # Get all branch org_ids
    branches = db.query(Branch).join(Company).filter(
        Company.tenant_id == current_tenant.id,
        Branch.is_active == True
    ).all()
    
    branch_orgs = [
        {
            "org_id": branch.branch_org_id,
            "type": "branch",
            "name": branch.name,
            "id": branch.id,
            "company_id": branch.company_id
        }
        for branch in branches
    ]
    
    return {
        "tenant": tenant_org,
        "companies": company_orgs,
        "branches": branch_orgs,
        "total": 1 + len(company_orgs) + len(branch_orgs)
    }

@router.get("/download-agent/{org_id}", tags=["tenant"])
async def download_agent(
    org_id: str,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_current_tenant)
):
    """
    Download agent MSI for a specific org_id
    
    Verifies that the org_id belongs to the tenant before allowing download.
    Returns the MSI installer file with embedded org_id configuration.
    """
    from fastapi.responses import FileResponse
    from pathlib import Path
    import shutil
    import zipfile
    import json
    import tempfile
    
    # Verify org_id belongs to tenant
    valid_org_id = False
    org_name = ""
    org_type = None
    
    # Check tenant org_id
    if current_tenant.tenant_org_id == org_id:
        valid_org_id = True
        org_name = current_tenant.name
        org_type = "TENANT"
    
    # Check company org_ids
    if not valid_org_id:
        company = db.query(Company).filter(
            Company.company_org_id == org_id,
            Company.tenant_id == current_tenant.id,
            Company.is_active == True
        ).first()
        if company:
            valid_org_id = True
            org_name = company.name
            org_type = "COMPANY"
    
    # Check branch org_ids
    if not valid_org_id:
        branch = db.query(Branch).join(Company).filter(
            Branch.branch_org_id == org_id,
            Company.tenant_id == current_tenant.id,
            Branch.is_active == True
        ).first()
        if branch:
            valid_org_id = True
            org_name = branch.name
            org_type = "BRANCH"
    
    if not valid_org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Org ID not found or does not belong to this tenant"
        )
    
    # Get paths - go up from backend/api/v1/endpoints/tenant.py to project root
    # tenant.py -> endpoints -> v1 -> api -> backend -> project_root
    # So we need to go up 4 levels to get to backend, then static is at backend/static/agents
    current_file = Path(__file__)
    # Go up 4 levels: endpoints -> v1 -> api -> backend
    backend_dir = current_file.parent.parent.parent.parent
    static_dir = backend_dir / "static" / "agents"
    msi_template = static_dir / "PrismTrackAgent.msi"
    
    # Check if files exist
    if not msi_template.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MSI template not found. Please ensure PrismTrackAgent.msi exists in backend/static/agents/"
        )
    
    # Return the MSI file for download
    # The MSI contains config.json template - installer script will update it with org_id
    # The org_id is embedded in the filename for user reference
    filename = f"PrismTrack_Agent_{org_id}.msi"
    
    # Ensure filename is clean (no trailing spaces or underscores)
    filename = filename.strip()
    
    # Use proper Content-Disposition header format
    # Using both standard and RFC 2231 format for maximum browser compatibility
    import urllib.parse
    encoded_filename = urllib.parse.quote(filename)
    
    return FileResponse(
        path=str(msi_template),
        filename=filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'
        }
    )

