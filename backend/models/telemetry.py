"""
Telemetry Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    window_title = Column(String(500))
    process_name = Column(String(255))
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    is_idle = Column(Boolean, default=False, nullable=False)
    screenshot_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="telemetry")

