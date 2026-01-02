"""Test Authentication Endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

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
    print("Testing PrismTrack Authentication System")
    print("=" * 60)
    
    # Test 1: Platform Admin Login
    print("\n" + "=" * 60)
    print("TEST 1: Platform Admin Login")
    print("=" * 60)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    result = test_endpoint("POST", "/auth/platform-admin/login", login_data)
    
    if result and "access_token" in result:
        platform_admin_token = result["access_token"]
        platform_admin_refresh = result["refresh_token"]
        print(f"\n✅ Platform Admin Token: {platform_admin_token[:50]}...")
        print(f"✅ Refresh Token: {platform_admin_refresh[:50]}...")
        
        # Test 2: Refresh Token
        print("\n" + "=" * 60)
        print("TEST 2: Refresh Token")
        print("=" * 60)
        refresh_data = {
            "refresh_token": platform_admin_refresh
        }
        refresh_result = test_endpoint("POST", "/auth/refresh", refresh_data)
        
        if refresh_result and "access_token" in refresh_result:
            print(f"\n✅ New Access Token: {refresh_result['access_token'][:50]}...")
    else:
        print("\n❌ Platform Admin login failed - cannot continue tests")
        print("   Make sure admin user exists: python scripts/create_admin.py")
    
    # Test 3: Tenant Login (will fail if no tenant exists, which is expected)
    print("\n" + "=" * 60)
    print("TEST 3: Tenant Login (Expected to fail - no tenant created yet)")
    print("=" * 60)
    tenant_login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    test_endpoint("POST", "/auth/tenant/login", tenant_login_data)
    
    print("\n" + "=" * 60)
    print("Authentication Tests Complete!")
    print("=" * 60)
    print("\n📚 Full API Documentation: http://localhost:8000/docs")
    print("📚 ReDoc: http://localhost:8000/redoc")

