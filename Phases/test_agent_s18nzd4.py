"""
Test PrismTrack Agent with org_id S18NZD4
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.database import SessionLocal
from backend.models.agent import Agent
from backend.models.telemetry import Telemetry
from datetime import datetime, timedelta

def test_agent():
    """Test agent registration and data collection"""
    db = SessionLocal()
    
    print("=" * 60)
    print("Testing PrismTrack Agent - Org ID: S18NZD4")
    print("=" * 60)
    print()
    
    # Check for agents with org_id S18NZD4
    agents = db.query(Agent).filter(Agent.org_id == 'S18NZD4').order_by(Agent.id.desc()).all()
    
    print(f"Found {len(agents)} agent(s) with org_id S18NZD4:")
    print()
    
    for agent in agents:
        print(f"Agent ID: {agent.id}")
        print(f"  Machine Name: {agent.machine_name}")
        print(f"  Hardware UUID: {agent.hardware_uuid[:30]}...")
        print(f"  Org Type: {agent.org_type}")
        print(f"  Status: {agent.status}")
        print(f"  Registered At: {agent.registered_at}")
        print(f"  Last Seen: {agent.last_seen}")
        
        # Check if agent is active (seen in last 2 minutes)
        if agent.last_seen:
            time_diff = datetime.now(agent.last_seen.tzinfo) - agent.last_seen
            is_active = time_diff.total_seconds() < 120  # 2 minutes
            print(f"  Is Active: {'YES' if is_active else 'NO'} (last seen {time_diff.total_seconds():.0f} seconds ago)")
        else:
            print(f"  Is Active: NO (never seen)")
        
        # Get telemetry count
        telemetry_count = db.query(Telemetry).filter(Telemetry.agent_id == agent.id).count()
        print(f"  Telemetry Records: {telemetry_count}")
        
        # Get recent telemetry
        recent_telemetry = db.query(Telemetry).filter(
            Telemetry.agent_id == agent.id
        ).order_by(Telemetry.timestamp.desc()).limit(5).all()
        
        if recent_telemetry:
            print(f"  Recent Telemetry (last 5):")
            for tel in recent_telemetry:
                window_title = tel.window_title[:50] if tel.window_title else "N/A"
                print(f"    - {tel.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {window_title}... (Idle: {tel.is_idle})")
        else:
            print(f"  No telemetry data yet")
        
        print()
    
    if not agents:
        print("⚠️  No agents found with org_id S18NZD4")
        print("   Make sure the agent is running and has registered with the backend")
        print()
    
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_agent()

