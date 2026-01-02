"""Test API endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code < 400:
            print(f"✅ Success")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            print(f"❌ Error: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Is the server running on {BASE_URL}?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Testing PrismTrack API")
    print("=" * 50)
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
    # Test health endpoint
    test_endpoint("GET", "/health")
    
    # Test docs endpoint
    print(f"\n📚 API Documentation available at: {BASE_URL}/docs")
    print(f"📚 ReDoc available at: {BASE_URL}/redoc")
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)

