#!/usr/bin/env python3
"""
Test script for the DigiLocker Mock API.

This script tests all the major endpoints of our mock DigiLocker API
to ensure everything is working correctly.
"""

import requests
import json
import sys
from typing import Dict, Any

# API Base URL
BASE_URL = "http://127.0.0.1:8000/api"

def print_response(response: requests.Response, endpoint: str) -> None:
    """Print formatted response for debugging."""
    print(f"\n{'='*50}")
    print(f"Testing: {endpoint}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print('='*50)

def test_health_check() -> bool:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health/")
        print_response(response, "Health Check")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_authentication_flow() -> Dict[str, Any]:
    """Test the complete authentication flow."""
    result = {"success": False, "session_token": None}
    
    # Step 1: Authenticate user
    auth_data = {"phone_number": "+919876543210"}
    try:
        response = requests.post(f"{BASE_URL}/digilocker/authenticate/", json=auth_data)
        print_response(response, "Authentication Request")
        
        if response.status_code != 200:
            return result
        
        auth_response = response.json()
        request_id = auth_response.get("request_id")
        mock_otp = auth_response.get("mock_otp")
        
        if not request_id or not mock_otp:
            print("Missing request_id or mock_otp in authentication response")
            return result
        
        # Step 2: Verify OTP
        otp_data = {"request_id": request_id, "otp_code": mock_otp}
        response = requests.post(f"{BASE_URL}/digilocker/verify-otp/", json=otp_data)
        print_response(response, "OTP Verification")
        
        if response.status_code != 200:
            return result
        
        verify_response = response.json()
        session_token = verify_response.get("session_token")
        
        if session_token:
            result["success"] = True
            result["session_token"] = session_token
        
    except Exception as e:
        print(f"Authentication flow failed: {e}")
    
    return result

def test_profile_endpoints(session_token: str) -> bool:
    """Test profile-related endpoints."""
    headers = {"Authorization": f"Bearer {session_token}"}
    
    try:
        # Test profile retrieval
        response = requests.get(f"{BASE_URL}/digilocker/profile/", headers=headers)
        print_response(response, "User Profile")
        
        if response.status_code != 200:
            return False
        
        # Test session info
        response = requests.get(f"{BASE_URL}/digilocker/session/", headers=headers)
        print_response(response, "Session Info")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Profile endpoints test failed: {e}")
        return False

def test_document_endpoints(session_token: str) -> bool:
    """Test document-related endpoints."""
    headers = {"Authorization": f"Bearer {session_token}"}
    
    try:
        # Test document list
        response = requests.get(f"{BASE_URL}/digilocker/documents/", headers=headers)
        print_response(response, "Document List")
        
        if response.status_code != 200:
            return False
        
        documents = response.json()
        if not documents:
            print("No documents found")
            return False
        
        # Test document download (use first document)
        doc_id = documents[0]["id"]
        response = requests.get(f"{BASE_URL}/digilocker/documents/{doc_id}/", headers=headers)
        print_response(response, f"Document Download ({doc_id})")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Document endpoints test failed: {e}")
        return False

def test_logout(session_token: str) -> bool:
    """Test logout endpoint."""
    headers = {"Authorization": f"Bearer {session_token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/digilocker/logout/", headers=headers)
        print_response(response, "Logout")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Logout test failed: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Starting DigiLocker Mock API Tests")
    print(f"Testing API at: {BASE_URL}")
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ Health check failed. Ensure the Django server is running.")
        sys.exit(1)
    
    print("✅ Health check passed")
    
    # Test 2: Authentication flow
    auth_result = test_authentication_flow()
    if not auth_result["success"]:
        print("❌ Authentication flow failed")
        sys.exit(1)
    
    print("✅ Authentication flow passed")
    session_token = auth_result["session_token"]
    
    # Test 3: Profile endpoints
    if not test_profile_endpoints(session_token):
        print("❌ Profile endpoints failed")
        sys.exit(1)
    
    print("✅ Profile endpoints passed")
    
    # Test 4: Document endpoints
    if not test_document_endpoints(session_token):
        print("❌ Document endpoints failed")
        sys.exit(1)
    
    print("✅ Document endpoints passed")
    
    # Test 5: Logout
    if not test_logout(session_token):
        print("❌ Logout failed")
        sys.exit(1)
    
    print("✅ Logout passed")
    
    print("\n🎉 All tests passed! DigiLocker Mock API is working correctly.")
    print("\n📝 API Documentation available at:")
    print(f"   • Swagger UI: http://127.0.0.1:8000/api/docs/")
    print(f"   • ReDoc: http://127.0.0.1:8000/api/redoc/")

if __name__ == "__main__":
    main()
