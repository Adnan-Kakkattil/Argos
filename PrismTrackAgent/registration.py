"""
Agent Registration with PrismTrack Backend
"""
import requests
import sys
from typing import Optional
from system_info import SystemInfo

def register_agent(api_base: str, org_id: str, system_info: SystemInfo) -> str:
    """
    Register agent with PrismTrack backend
    
    Args:
        api_base: Base URL of the API (e.g., "http://localhost:8000/api/v1")
        org_id: Organization ID to register with
        system_info: SystemInfo object with machine details
    
    Returns:
        agent_token: Token to use for subsequent API calls
    
    Raises:
        Exception: If registration fails
    """
    url = f"{api_base}/agent/register"
    
    # Backend requires org_type, but will auto-detect from org_id
    # We'll send "TENANT" as default, backend will override if needed
    payload = {
        "org_id": org_id,
        "org_type": "TENANT",  # Required field, backend will auto-detect actual type
        "machine_name": system_info.machine_name,
        "hardware_uuid": system_info.hardware_uuid
    }
    
    print(f"Registering agent with backend: {url}")
    print(f"  Org ID: {org_id}")
    print(f"  Machine Name: {system_info.machine_name}")
    print(f"  Hardware UUID: {system_info.hardware_uuid}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        agent_token = data.get('agent_token')
        
        if not agent_token:
            raise Exception("No agent_token received from backend")
        
        print(f"Agent registered successfully!")
        print(f"  Agent ID: {data.get('agent_id')}")
        print(f"  Message: {data.get('message')}")
        
        return agent_token
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to register agent: {e}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('detail', 'Unknown error')
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"Registration error: {e}")

