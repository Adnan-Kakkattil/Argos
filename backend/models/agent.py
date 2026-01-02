"""
Agent Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base
import enum

class OrgType(str, enum.Enum):
    TENANT = "TENANT"
    COMPANY = "COMPANY"
    BRANCH = "BRANCH"

class AgentStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    org_id = Column(String(8), nullable=False, index=True)  # Can be tenant, company, or branch org_id
    org_type = Column(SQLEnum(OrgType), nullable=False)
    machine_name = Column(String(255), nullable=False)
    hardware_uuid = Column(String(255), unique=True, index=True, nullable=False)
    agent_token = Column(String(255), unique=True, index=True, nullable=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.OFFLINE, nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    telemetry = relationship("Telemetry", back_populates="agent", cascade="all, delete-orphan")

