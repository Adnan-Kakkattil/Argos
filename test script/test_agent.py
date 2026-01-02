"""Test Agent Endpoints"""
import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api/v1"

def get_platform_admin_token():
    """Get platform admin auth token"""
    response = requests.post(
        f"{BASE_URL}/auth/platform-admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_tenant_token(email, password):
    """Get tenant auth token"""
    response = requests.post(
        f"{BASE_URL}/auth/tenant/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_endpoint(method, endpoint, data=None, token=None, headers=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    request_headers = {}
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    if headers:
        request_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=request_headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=request_headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=request_headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=request_headers, timeout=5)
        else:
            print(f"[ERROR] Unsupported method: {method}")
            return None
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"[OK] Success")
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                return result
            except:
                if response.status_code == 204:
                    print("✅ No content (successful deletion)")
                else:
                    print(f"Response: {response.text[:200]}")
                return None
        else:
            print(f"[ERROR] Error: {response.text[:200]}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection failed - Is the server running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Agent Endpoints")
    print("=" * 60)
    
    # Step 1: Create a tenant and get org_id
    print("\n" + "=" * 60)
    print("STEP 1: Create Tenant (Platform Admin)")
    print("=" * 60)
    platform_token = get_platform_admin_token()
    if not platform_token:
        print("[ERROR] Failed to authenticate as platform admin")
        exit(1)
    
    import time
    unique_id = int(time.time())
    tenant_data = {
        "name": f"Agent Test Corp {unique_id}",
        "admin_email": f"agent{unique_id}@testcorp.com",
        "admin_password": "Agent123!",
    }
    tenant_result = test_endpoint("POST", "/platform-admin/tenants", tenant_data, platform_token)
    
    if not tenant_result:
        print("❌ Failed to create tenant")
        exit(1)
    
    tenant_org_id = tenant_result.get("tenant_org_id")
    tenant_email = tenant_data["admin_email"]
    tenant_password = tenant_data["admin_password"]
    print(f"[OK] Tenant created with Org ID: {tenant_org_id}")
    
    # Step 2: Register Agent
    print("\n" + "=" * 60)
    print("STEP 2: Register Agent")
    print("=" * 60)
    import time
    unique_hw_uuid = f"test-hardware-uuid-{int(time.time())}"
    agent_register_data = {
        "org_id": tenant_org_id,
        "org_type": "TENANT",
        "machine_name": "TEST-MACHINE-01",
        "hardware_uuid": unique_hw_uuid
    }
    register_result = test_endpoint("POST", "/agent/register", agent_register_data)
    
    agent_token = None
    agent_id = None
    if register_result:
        agent_token = register_result.get("agent_token")
        agent_id = register_result.get("agent_id")
        print(f"[OK] Agent registered with ID: {agent_id}")
        print(f"[OK] Agent Token: {agent_token[:50]}...")
    
    if not agent_token:
        print("[ERROR] Failed to register agent")
        exit(1)
    
    # Step 3: Agent Heartbeat
    print("\n" + "=" * 60)
    print("STEP 3: Agent Heartbeat")
    print("=" * 60)
    heartbeat_data = {
        "agent_token": agent_token,
        "status": "ONLINE"
    }
    heartbeat_headers = {"X-Agent-Token": agent_token}
    test_endpoint("POST", "/agent/heartbeat", heartbeat_data, headers=heartbeat_headers)
    
    # Step 4: Submit Telemetry
    print("\n" + "=" * 60)
    print("STEP 4: Submit Telemetry")
    print("=" * 60)
    telemetry_data = {
        "agent_token": agent_token,
        "telemetry": [
            {
                "window_title": "Visual Studio Code",
                "process_name": "Code.exe",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_idle": False,
                "screenshot_url": None
            },
            {
                "window_title": "Chrome - Google",
                "process_name": "chrome.exe",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_idle": False,
                "screenshot_url": None
            },
            {
                "window_title": "Desktop",
                "process_name": "explorer.exe",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "is_idle": True,
                "screenshot_url": None
            }
        ]
    }
    telemetry_headers = {"X-Agent-Token": agent_token}
    test_endpoint("POST", "/agent/telemetry", telemetry_data, headers=telemetry_headers)
    
    # Step 5: List Agents
    print("\n" + "=" * 60)
    print("STEP 5: List Agents")
    print("=" * 60)
    test_endpoint("GET", f"/agent/agents?org_id={tenant_org_id}")
    
    # Step 6: Get Agent Details
    if agent_id:
        print("\n" + "=" * 60)
        print("STEP 6: Get Agent Details")
        print("=" * 60)
        test_endpoint("GET", f"/agent/agents/{agent_id}")
    
    # Step 7: Multiple Heartbeats (simulate agent running)
    print("\n" + "=" * 60)
    print("STEP 7: Multiple Heartbeats (Simulating Agent Running)")
    print("=" * 60)
    for i in range(3):
        heartbeat_data = {
            "agent_token": agent_token,
            "status": "ONLINE"
        }
        heartbeat_headers = {"X-Agent-Token": agent_token}
        result = test_endpoint("POST", "/agent/heartbeat", heartbeat_data, headers=heartbeat_headers)
        if result:
            print(f"  Heartbeat {i+1}: [OK]")
    
    print("\n" + "=" * 60)
    print("Agent Tests Complete!")
    print("=" * 60)
    print("\n📚 Full API Documentation: http://localhost:8000/docs")

