"""
Tenant Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tenant_org_id = Column(String(8), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    admin_email = Column(String(255), nullable=False, index=True)
    admin_password_hash = Column(String(255), nullable=False)
    admin_api_key = Column(String(255), unique=True, index=True, nullable=False)
    created_by = Column(Integer, ForeignKey("platform_admins.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    companies = relationship("Company", back_populates="tenant", cascade="all, delete-orphan")
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")

