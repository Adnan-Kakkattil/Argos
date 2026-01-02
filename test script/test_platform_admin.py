"""Test Platform Admin Endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    """Get platform admin auth token"""
    response = requests.post(
        f"{BASE_URL}/auth/platform-admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_endpoint(method, endpoint, data=None, token=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"✅ Success")
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
            print(f"❌ Error: {response.text[:200]}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Is the server running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Platform Admin Endpoints")
    print("=" * 60)
    
    # Get auth token
    print("\n🔐 Authenticating as Platform Admin...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate. Make sure admin user exists.")
        exit(1)
    print("✅ Authenticated successfully")
    
    # Test 1: List tenants (should be empty initially)
    print("\n" + "=" * 60)
    print("TEST 1: List Tenants")
    print("=" * 60)
    tenants_result = test_endpoint("GET", "/platform-admin/tenants", token=token)
    
    # Test 2: Create tenant
    print("\n" + "=" * 60)
    print("TEST 2: Create New Tenant")
    print("=" * 60)
    tenant_data = {
        "name": "Acme Corporation",
        "admin_email": "admin@acme.com",
        "admin_password": "Acme123!",
        "company_name": "Acme Corporation",
        "address": "123 Business St, New York, NY 10001",
        "phone": "+1-555-0123",
        "industry_type": "Technology"
    }
    tenant_result = test_endpoint("POST", "/platform-admin/tenants", tenant_data, token=token)
    
    tenant_id = None
    if tenant_result:
        tenant_id = tenant_result.get("id")
        print(f"\n✅ Tenant created with ID: {tenant_id}")
        print(f"✅ Tenant Org ID: {tenant_result.get('tenant_org_id')}")
        print(f"✅ Admin API Key: {tenant_result.get('admin_api_key')}")
    
    # Test 3: Get tenant details
    if tenant_id:
        print("\n" + "=" * 60)
        print("TEST 3: Get Tenant Details")
        print("=" * 60)
        test_endpoint("GET", f"/platform-admin/tenants/{tenant_id}", token=token)
    
    # Test 4: Get tenant stats (Client 360)
    if tenant_id:
        print("\n" + "=" * 60)
        print("TEST 4: Get Tenant Stats (Client 360)")
        print("=" * 60)
        test_endpoint("GET", f"/platform-admin/tenants/{tenant_id}/stats", token=token)
    
    # Test 5: List tenants again (should have 1 now)
    print("\n" + "=" * 60)
    print("TEST 5: List Tenants (After Creation)")
    print("=" * 60)
    test_endpoint("GET", "/platform-admin/tenants", token=token)
    
    # Test 6: Update tenant
    if tenant_id:
        print("\n" + "=" * 60)
        print("TEST 6: Update Tenant")
        print("=" * 60)
        update_data = {
            "name": "Acme Corporation Updated"
        }
        test_endpoint("PUT", f"/platform-admin/tenants/{tenant_id}", update_data, token=token)
    
    print("\n" + "=" * 60)
    print("Platform Admin Tests Complete!")
    print("=" * 60)
    print("\n📚 Full API Documentation: http://localhost:8000/docs")

