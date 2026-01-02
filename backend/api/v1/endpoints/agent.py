"""
Agent Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone
from backend.core.database import get_db
from backend.core.security import generate_api_key
from backend.models.agent import Agent, OrgType, AgentStatus
from backend.models.tenant import Tenant
from backend.models.company import Company
from backend.models.branch import Branch
from backend.models.telemetry import Telemetry
from backend.schemas.agent import (
    AgentRegister,
    AgentRegisterResponse,
    AgentHeartbeat,
    TelemetrySubmit,
    TelemetryData,
    AgentResponse,
    AgentListResponse
)

router = APIRouter()

def get_agent_from_token(
    x_agent_token: str = Header(..., alias="X-Agent-Token"),
    db: Session = Depends(get_db)
) -> Agent:
    """
    Verify agent token and return agent instance
    
    Args:
        x_agent_token: Agent token from X-Agent-Token header
        db: Database session
        
    Returns:
        Agent instance
        
    Raises:
        HTTPException: If token is invalid or agent not found
    """
    agent = db.query(Agent).filter(Agent.agent_token == x_agent_token).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent token"
        )
    
    return agent

@router.post("/register", response_model=AgentRegisterResponse, tags=["agent"])
async def register_agent(
    agent_data: AgentRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new agent
    
    Validates the org_id and creates an agent record with a unique agent_token.
    The agent uses this token for all subsequent API calls.
    """
    # Verify org_id exists and get org_type
    org_type = None
    org_id_valid = False
    
    # Check tenant org_id
    tenant = db.query(Tenant).filter(
        Tenant.tenant_org_id == agent_data.org_id,
        Tenant.is_active == True
    ).first()
    if tenant:
        org_type = OrgType.TENANT
        org_id_valid = True
    
    # Check company org_id
    if not org_id_valid:
        company = db.query(Company).filter(
            Company.company_org_id == agent_data.org_id,
            Company.is_active == True
        ).first()
        if company:
            org_type = OrgType.COMPANY
            org_id_valid = True
    
    # Check branch org_id
    if not org_id_valid:
        branch = db.query(Branch).filter(
            Branch.branch_org_id == agent_data.org_id,
            Branch.is_active == True
        ).first()
        if branch:
            org_type = OrgType.BRANCH
            org_id_valid = True
    
    if not org_id_valid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid org_id. Org ID not found or inactive."
        )
    
    # Check if agent with same hardware_uuid already exists
    existing_agent = db.query(Agent).filter(
        Agent.hardware_uuid == agent_data.hardware_uuid
    ).first()
    
    if existing_agent:
        # Update existing agent
        existing_agent.org_id = agent_data.org_id
        existing_agent.org_type = org_type or existing_agent.org_type
        existing_agent.machine_name = agent_data.machine_name
        existing_agent.last_seen = datetime.now(timezone.utc)
        existing_agent.status = AgentStatus.ONLINE
        
        db.commit()
        db.refresh(existing_agent)
        
        return {
            "agent_id": existing_agent.id,
            "agent_token": existing_agent.agent_token,
            "message": "Agent updated successfully"
        }
    
    # Generate unique agent token
    agent_token = generate_api_key()
    
    # Ensure token is unique
    while db.query(Agent).filter(Agent.agent_token == agent_token).first():
        agent_token = generate_api_key()
    
    # Use detected org_type or fallback to provided one
    # Ensure we have a valid OrgType enum value
    if org_type:
        final_org_type = org_type
    else:
        # Convert string to enum if needed
        if isinstance(agent_data.org_type, str):
            # Convert to uppercase to match database enum
            try:
                final_org_type = OrgType(agent_data.org_type.upper())
            except ValueError:
                # If invalid, default to tenant
                final_org_type = OrgType.TENANT
        else:
            final_org_type = agent_data.org_type
    
    # Create new agent
    try:
        agent = Agent(
            org_id=agent_data.org_id,
            org_type=final_org_type,
            machine_name=agent_data.machine_name,
            hardware_uuid=agent_data.hardware_uuid,
            agent_token=agent_token,
            last_seen=datetime.now(timezone.utc),
            status=AgentStatus.ONLINE
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent: {str(e)}"
        )
    
    try:
        db.add(agent)
        db.commit()
        db.refresh(agent)
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving agent to database: {str(e)}\n{error_details}"
        )
    
    return {
        "agent_id": agent.id,
        "agent_token": agent_token,
        "message": "Agent registered successfully"
    }

@router.post("/heartbeat", tags=["agent"])
async def agent_heartbeat(
    heartbeat_data: AgentHeartbeat,
    db: Session = Depends(get_db),
    agent: Agent = Depends(get_agent_from_token)
):
    """
    Agent heartbeat endpoint
    
    Updates agent's last_seen timestamp and status.
    Agents should call this endpoint periodically (every 30-60 seconds).
    """
    agent.last_seen = datetime.utcnow()
    
    if heartbeat_data.status:
        agent.status = heartbeat_data.status
    else:
        agent.status = AgentStatus.ONLINE
    
    db.commit()
    
    return {
        "status": "ok",
        "message": "Heartbeat received",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/telemetry", tags=["agent"])
async def submit_telemetry(
    telemetry_data: TelemetrySubmit,
    db: Session = Depends(get_db),
    agent: Agent = Depends(get_agent_from_token)
):
    """
    Submit telemetry data from agent
    
    Accepts multiple telemetry records in a single request.
    Each record includes window title, process name, timestamp, idle status, and optional screenshot URL.
    
    Note: Agent token is verified via X-Agent-Token header, but can also be included in body for compatibility.
    """
    # Verify agent token matches (if provided in body)
    if telemetry_data.agent_token and agent.agent_token != telemetry_data.agent_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent token mismatch"
        )
    
    # Create telemetry records
    telemetry_records = []
    for tel_data in telemetry_data.telemetry:
        telemetry = Telemetry(
            agent_id=agent.id,
            window_title=tel_data.window_title,
            process_name=tel_data.process_name,
            timestamp=tel_data.timestamp,
            is_idle=tel_data.is_idle,
            screenshot_url=tel_data.screenshot_url
        )
        telemetry_records.append(telemetry)
        db.add(telemetry)
    
    # Update agent last_seen
    agent.last_seen = datetime.now(timezone.utc)
    agent.status = AgentStatus.ONLINE
    
    db.commit()
    
    return {
        "status": "ok",
        "message": f"Telemetry data received: {len(telemetry_records)} records",
        "records_count": len(telemetry_records),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/agents", response_model=AgentListResponse, tags=["agent"])
async def list_agents(
    org_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all agents (for platform/tenant admin use)
    
    Can filter by org_id if provided.
    """
    query = db.query(Agent)
    
    if org_id:
        query = query.filter(Agent.org_id == org_id)
    
    agents = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "agents": agents,
        "total": total
    }

@router.get("/agents/{agent_id}", response_model=AgentResponse, tags=["agent"])
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    """
    Get agent details by ID
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent

