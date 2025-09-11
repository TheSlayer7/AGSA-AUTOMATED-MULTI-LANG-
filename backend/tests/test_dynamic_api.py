#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.safe_logging import mask_phone_number, mask_name, mask_address

"""
Test script for dynamic DigiLocker API with database-backed documents.

This script tests the DigiLocker API endpoints using the database-driven
document management system.
"""

import requests
import json
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    """Test the DigiLocker API endpoints."""
    
    print("🧪 Testing Dynamic DigiLocker API")
    print("=" * 50)
    
    # Test 1: Request OTP
    print("\n1. Testing OTP Request...")
    phone_number = "+919876543210"  # From our sample data
    
    try:
        response = requests.post(f"{BASE_URL}/auth/request-otp/", json={
            "phone_number": phone_number
        })
        
        if response.status_code == 200:
            otp_data = response.json()
            print(f"✅ OTP requested successfully")
            print(f"   Request ID: {otp_data['request_id']}")
            request_id = otp_data['request_id']
        else:
            print(f"❌ OTP request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error requesting OTP: {e}")
        return
    
    # Test 2: Verify OTP (using the OTP from console output)
    print("\n2. Testing OTP Verification...")
    # The OTP will be printed in the server console when requested
    # For testing, let's check the database for the actual OTP
    
    # Get the OTP from the database (for testing purposes)
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
    django.setup()
    
    from api.models import OTPRequest
    try:
        otp_request = OTPRequest.objects.get(request_id=request_id)
        otp_code = otp_request.otp_code
        print(f"📱 Using OTP: {otp_code}")
    except Exception as e:
        print(f"❌ Could not get OTP from database: {e}")
        return
    
    try:
        response = requests.post(f"{BASE_URL}/auth/verify-otp/", json={
            "request_id": request_id,
            "otp": otp_code
        })
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ OTP verified successfully")
            print(f"   Session Token: {auth_data['session_token'][:16]}...")
            print(f"   User ID: {auth_data['user_id']}")
            session_token = auth_data['session_token']
        else:
            print(f"❌ OTP verification failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error verifying OTP: {e}")
        return
    
    # Test 3: Get user info
    print("\n3. Testing User Info Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/user/profile/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User info retrieved successfully")
            print(f"   Name: {mask_name(user_data['name'])}")
            print(f"   Phone: {mask_phone_number(user_data['phone_number'])}")
            print(f"   Address: {mask_address(user_data['address'])}")
        else:
            print(f"❌ User info retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
    
    # Test 4: List documents
    print("\n4. Testing Document Listing...")
    try:
        response = requests.get(f"{BASE_URL}/documents/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documents listed successfully")
            print(f"   Found {len(documents)} documents")
            
            for i, doc in enumerate(documents[:3], 1):  # Show first 3
                print(f"   {i}. {doc['name']} ({doc['type']})")
                print(f"      ID: {doc['doc_id']}")
                print(f"      Size: {doc['size']} bytes")
                print(f"      Verified: {doc['is_verified']}")
            
            if documents:
                doc_id = documents[0]['doc_id']
                
                # Test 5: Download document
                print(f"\n5. Testing Document Download...")
                try:
                    response = requests.get(f"{BASE_URL}/documents/{doc_id}/download/", headers={
                        "Authorization": f"Bearer {session_token}"
                    })
                    
                    if response.status_code == 200:
                        print(f"✅ Document downloaded successfully")
                        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
                        print(f"   Size: {len(response.content)} bytes")
                        print(f"   Filename: {response.headers.get('Content-Disposition', 'Not specified')}")
                    else:
                        print(f"❌ Document download failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error downloading document: {e}")
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print("\n📝 Next Steps:")
    print("1. Visit admin panel: http://127.0.0.1:8000/admin/")
    print("2. Upload documents via Django admin")
    print("3. Test API with uploaded documents")
    print("4. Build frontend for document management")


if __name__ == '__main__':
    test_api()
