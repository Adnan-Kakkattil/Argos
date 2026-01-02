"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.core.database import get_db
from backend.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from backend.schemas.auth import Token, PlatformAdminLogin, TenantLogin
from backend.models.platform_admin import PlatformAdmin
from backend.models.tenant import Tenant
from datetime import timedelta
from backend.core.config import settings

router = APIRouter()

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/platform-admin/login", response_model=Token, tags=["authentication"])
async def platform_admin_login(
    credentials: PlatformAdminLogin,
    db: Session = Depends(get_db)
):
    """
    Platform Admin Login
    
    Authenticate platform admin and return JWT tokens
    """
    # Find admin by username or email
    admin = db.query(PlatformAdmin).filter(
        (PlatformAdmin.username == credentials.username) |
        (PlatformAdmin.email == credentials.username)
    ).first()
    
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(admin.id),  # JWT requires sub to be a string
            "username": admin.username,
            "email": admin.email,
            "type": "platform_admin"
        },
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(admin.id),  # JWT requires sub to be a string
            "username": admin.username,
            "type": "platform_admin"
        }
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/tenant/login", response_model=Token, tags=["authentication"])
async def tenant_login(
    credentials: TenantLogin,
    db: Session = Depends(get_db)
):
    """
    Tenant Admin Login
    
    Authenticate tenant admin and return JWT tokens
    """
    # Find tenant by email
    tenant = db.query(Tenant).filter(
        Tenant.admin_email == credentials.email
    ).first()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, tenant.admin_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(tenant.id),  # JWT requires sub to be a string
            "tenant_org_id": tenant.tenant_org_id,
            "email": tenant.admin_email,
            "type": "tenant"
        },
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(tenant.id),  # JWT requires sub to be a string
            "tenant_org_id": tenant.tenant_org_id,
            "type": "tenant"
        }
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token, tags=["authentication"])
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh Access Token
    
    Use refresh token to get a new access token
    """
    payload = verify_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject"
        )
    
    # Convert string back to int for database query
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: invalid subject"
        )
    
    # Get the original user type from the payload
    original_type = payload.get("original_type")
    
    # Fallback: Try to determine type from payload keys
    if not original_type:
        if "username" in payload:
            original_type = "platform_admin"
        elif "tenant_org_id" in payload:
            original_type = "tenant"
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
    
    if original_type == "platform_admin":
        admin = db.query(PlatformAdmin).filter(PlatformAdmin.id == user_id).first()
        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found or inactive"
            )
        
        access_token = create_access_token(
            data={
                "sub": str(admin.id),
                "username": admin.username,
                "email": admin.email,
                "type": "platform_admin"
            }
        )
        
        new_refresh_token = create_refresh_token(
            data={
                "sub": str(admin.id),
                "username": admin.username,
                "type": "platform_admin"
            }
        )
    
    elif original_type == "tenant":
        tenant = db.query(Tenant).filter(Tenant.id == user_id).first()
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant not found or inactive"
            )
        
        access_token = create_access_token(
            data={
                "sub": str(tenant.id),
                "tenant_org_id": tenant.tenant_org_id,
                "email": tenant.admin_email,
                "type": "tenant"
            }
        )
        
        new_refresh_token = create_refresh_token(
            data={
                "sub": str(tenant.id),
                "tenant_org_id": tenant.tenant_org_id,
                "type": "tenant"
            }
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

