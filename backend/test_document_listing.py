#!/usr/bin/env python3
"""
Test the fixed document listing API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_document_listing():
    print("🧪 Testing Document Listing API...")
    
    # Step 1: Authenticate
    print("1. Requesting OTP...")
    otp_response = requests.post(f"{BASE_URL}/auth/request-otp/", json={
        "phone": "9876543210"
    })
    
    if otp_response.status_code != 200:
        print(f"❌ OTP request failed: {otp_response.text}")
        return
    
    print("✅ OTP requested successfully")
    
    # Step 2: Verify OTP (using test OTP)
    print("2. Verifying OTP...")
    verify_response = requests.post(f"{BASE_URL}/auth/verify-otp/", json={
        "phone": "9876543210",
        "otp": "123456"  # Test OTP
    })
    
    if verify_response.status_code != 200:
        print(f"❌ OTP verification failed: {verify_response.text}")
        return
    
    session_token = verify_response.json()["session_token"]
    headers = {"x-session-token": session_token}
    print("✅ OTP verified successfully")
    
    # Step 3: Test document listing (this was failing before)
    print("3. Testing document listing...")
    docs_response = requests.get(f"{BASE_URL}/documents/", headers=headers)
    
    print(f"Status Code: {docs_response.status_code}")
    
    if docs_response.status_code == 200:
        docs_data = docs_response.json()
        print("✅ Document listing successful!")
        print(f"📄 Number of documents: {len(docs_data.get('documents', []))}")
        
        if docs_data.get('documents'):
            for doc in docs_data['documents']:
                print(f"  - {doc['name']} (ID: {doc['doc_id']}, Size: {doc['size']} bytes)")
        else:
            print("  📋 No documents found (database is clean)")
    else:
        print(f"❌ Document listing failed: {docs_response.text}")
        return False
    
    # Step 4: Test document types
    print("4. Testing document types...")
    types_response = requests.get(f"{BASE_URL}/documents/types/")
    
    if types_response.status_code == 200:
        print("✅ Document types retrieved successfully")
        types_data = types_response.json()
        print(f"📋 Available document types: {len(types_data)}")
    else:
        print(f"❌ Document types failed: {types_response.text}")
    
    return True

if __name__ == "__main__":
    success = test_document_listing()
    if success:
        print("\n🎉 All tests passed! The 500 error has been fixed.")
    else:
        print("\n❌ Tests failed. Check the error messages above.")
