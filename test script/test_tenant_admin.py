"""Test Tenant Admin Endpoints"""
import requests
import json

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
    print("Testing Tenant Admin Endpoints")
    print("=" * 60)
    
    # Step 1: Create a tenant using platform admin
    print("\n" + "=" * 60)
    print("STEP 1: Create Tenant (Platform Admin)")
    print("=" * 60)
    platform_token = get_platform_admin_token()
    if not platform_token:
        print("❌ Failed to authenticate as platform admin")
        exit(1)
    
    tenant_data = {
        "name": "Test Corporation",
        "admin_email": "tenant@testcorp.com",
        "admin_password": "Test123!",
        "company_name": "Test Corporation",
        "address": "456 Test Ave",
        "phone": "+1-555-9999",
        "industry_type": "Testing"
    }
    tenant_result = test_endpoint("POST", "/platform-admin/tenants", tenant_data, platform_token)
    
    if not tenant_result:
        print("❌ Failed to create tenant")
        exit(1)
    
    tenant_email = tenant_data["admin_email"]
    tenant_password = tenant_data["admin_password"]
    tenant_org_id = tenant_result.get("tenant_org_id")
    
    print(f"\n✅ Tenant created:")
    print(f"   Email: {tenant_email}")
    print(f"   Org ID: {tenant_org_id}")
    
    # Step 2: Login as tenant
    print("\n" + "=" * 60)
    print("STEP 2: Login as Tenant")
    print("=" * 60)
    tenant_token = get_tenant_token(tenant_email, tenant_password)
    if not tenant_token:
        print("❌ Failed to authenticate as tenant")
        exit(1)
    print("✅ Authenticated as tenant")
    
    # Step 3: Create Company
    print("\n" + "=" * 60)
    print("STEP 3: Create Company")
    print("=" * 60)
    company_data = {"name": "Test Company"}
    company_result = test_endpoint("POST", "/tenant/companies", company_data, tenant_token)
    
    company_id = None
    company_org_id = None
    if company_result:
        company_id = company_result.get("id")
        company_org_id = company_result.get("company_org_id")
        print(f"✅ Company created with ID: {company_id}, Org ID: {company_org_id}")
    
    # Step 4: Create Branch
    if company_id:
        print("\n" + "=" * 60)
        print("STEP 4: Create Branch")
        print("=" * 60)
        branch_data = {
            "name": "Test Branch",
            "location": "New York, NY",
            "ip_addresses": "192.168.1.1,192.168.1.2"
        }
        branch_result = test_endpoint("POST", f"/tenant/companies/{company_id}/branches", branch_data, tenant_token)
        
        branch_id = None
        branch_org_id = None
        if branch_result:
            branch_id = branch_result.get("id")
            branch_org_id = branch_result.get("branch_org_id")
            print(f"✅ Branch created with ID: {branch_id}, Org ID: {branch_org_id}")
    
    # Step 5: Create User
    print("\n" + "=" * 60)
    print("STEP 5: Create User")
    print("=" * 60)
    user_data = {
        "username": "testuser",
        "email": "user@testcorp.com",
        "password": "User123!",
        "role": "admin"
    }
    user_result = test_endpoint("POST", "/tenant/users", user_data, tenant_token)
    
    user_id = None
    if user_result:
        user_id = user_result.get("id")
        print(f"✅ User created with ID: {user_id}")
    
    # Step 6: List Companies
    print("\n" + "=" * 60)
    print("STEP 6: List Companies")
    print("=" * 60)
    test_endpoint("GET", "/tenant/companies", token=tenant_token)
    
    # Step 7: List Branches
    if company_id:
        print("\n" + "=" * 60)
        print("STEP 7: List Branches")
        print("=" * 60)
        test_endpoint("GET", f"/tenant/companies/{company_id}/branches", token=tenant_token)
    
    # Step 8: List Users
    print("\n" + "=" * 60)
    print("STEP 8: List Users")
    print("=" * 60)
    test_endpoint("GET", "/tenant/users", token=tenant_token)
    
    # Step 9: List Org IDs
    print("\n" + "=" * 60)
    print("STEP 9: List Org IDs (for Agent Download)")
    print("=" * 60)
    org_ids_result = test_endpoint("GET", "/tenant/org-ids", token=tenant_token)
    
    # Step 10: Download Agent (Tenant)
    if tenant_org_id:
        print("\n" + "=" * 60)
        print("STEP 10: Download Agent (Tenant Org ID)")
        print("=" * 60)
        test_endpoint("GET", f"/tenant/download-agent/{tenant_org_id}", token=tenant_token)
    
    # Step 11: Download Agent (Company)
    if company_org_id:
        print("\n" + "=" * 60)
        print("STEP 11: Download Agent (Company Org ID)")
        print("=" * 60)
        test_endpoint("GET", f"/tenant/download-agent/{company_org_id}", token=tenant_token)
    
    # Step 12: Download Agent (Branch)
    if branch_org_id:
        print("\n" + "=" * 60)
        print("STEP 12: Download Agent (Branch Org ID)")
        print("=" * 60)
        test_endpoint("GET", f"/tenant/download-agent/{branch_org_id}", token=tenant_token)
    
    print("\n" + "=" * 60)
    print("Tenant Admin Tests Complete!")
    print("=" * 60)
    print("\n📚 Full API Documentation: http://localhost:8000/docs")

