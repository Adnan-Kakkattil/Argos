"""
Agent Version Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.sql import func
from backend.core.database import Base

class AgentVersion(Base):
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version_number = Column(String(50), unique=True, nullable=False, index=True)
    changelog = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to zip file in static/agents/versions/
    file_size = Column(BigInteger, nullable=False)  # File size in bytes
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash for integrity
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_latest = Column(Boolean, default=False, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey('platform_admins.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)  # When version was released

