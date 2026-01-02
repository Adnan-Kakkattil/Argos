"""
Branch Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    branch_org_id = Column(String(8), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    ip_addresses = Column(Text)  # JSON array of IPs stored as text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="branches")

