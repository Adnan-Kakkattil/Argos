"""
Script to help restart the backend server
This script checks if the backend is running and provides instructions
"""
import requests
import sys

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Backend is running on http://localhost:8000")
            return True
    except:
        pass
    print("❌ Backend is not running")
    return False

def main():
    print("=" * 60)
    print("Backend Server Status Check")
    print("=" * 60)
    
    is_running = check_backend()
    
    if is_running:
        print("\n⚠️  Backend is running but may need restart for CORS changes")
        print("\nTo restart:")
        print("1. Stop the current server (Ctrl+C in the terminal running it)")
        print("2. Run: python -m backend.main")
        print("   Or: uvicorn backend.main:app --reload")
    else:
        print("\nTo start the backend:")
        print("  python -m backend.main")
        print("  Or: uvicorn backend.main:app --reload")
    
    print("\n" + "=" * 60)
    print("CORS Configuration Check")
    print("=" * 60)
    
    try:
        from backend.core.config import settings
        print(f"CORS Origins: {settings.CORS_ORIGINS}")
        if "http://localhost:8080" in settings.CORS_ORIGINS:
            print("✅ Port 8080 is in CORS origins")
        else:
            print("❌ Port 8080 is NOT in CORS origins")
            print("   Update .env file: CORS_ORIGINS=...,http://localhost:8080")
    except Exception as e:
        print(f"Error checking CORS config: {e}")

if __name__ == "__main__":
    main()

