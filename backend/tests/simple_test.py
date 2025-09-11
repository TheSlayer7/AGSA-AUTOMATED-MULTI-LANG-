#!/usr/bin/env python
"""
Simple test for the DigiLocker API endpoints.
"""

import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoints():
    """Test basic API endpoints."""
    
    print("🧪 Testing DigiLocker API Endpoints")
    print("=" * 40)
    
    # Test health check (if available)
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print("⚠️  API returned non-200 status")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test OTP request with sample data
    print("\n2. Testing OTP request...")
    try:
        response = requests.post(f"{BASE_URL}/digilocker/authenticate/", json={
            "phone_number": "+919876543210"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:100]}...")
        
        if response.status_code == 200:
            print("✅ OTP request successful")
        else:
            print("⚠️  OTP request failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("📝 To test further:")
    print("1. Check Django admin at http://127.0.0.1:8000/admin/")
    print("2. Upload documents via admin interface")
    print("3. Use the OTP from server console for verification")

if __name__ == '__main__':
    test_endpoints()
