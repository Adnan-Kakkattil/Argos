"""
Agent Schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from backend.models.agent import OrgType, AgentStatus

class AgentRegister(BaseModel):
    org_id: str
    org_type: OrgType
    machine_name: str
    hardware_uuid: str

class AgentRegisterResponse(BaseModel):
    agent_id: int
    agent_token: str
    message: str

class AgentHeartbeat(BaseModel):
    agent_token: str
    status: Optional[AgentStatus] = None

class TelemetryData(BaseModel):
    window_title: Optional[str] = None
    process_name: Optional[str] = None
    timestamp: datetime
    is_idle: bool = False
    screenshot_url: Optional[str] = None

class TelemetrySubmit(BaseModel):
    agent_token: str
    telemetry: List[TelemetryData]

class HeartbeatResponse(BaseModel):
    status: str
    message: str
    timestamp: str

class TelemetryResponse(BaseModel):
    status: str
    message: str
    records_count: int
    timestamp: str

class AgentResponse(BaseModel):
    id: int
    org_id: str
    org_type: OrgType
    machine_name: str
    hardware_uuid: str
    last_seen: datetime
    status: AgentStatus
    registered_at: datetime
    
    class Config:
        from_attributes = True

class AgentListResponse(BaseModel):
    agents: List[AgentResponse]
    total: int

