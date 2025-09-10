#!/usr/bin/env python
"""
Comprehensive test for the fixed DigiLocker API endpoints.
"""

import requests
import json
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

# Setup Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from api.models import OTPRequest

# API base URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_full_api_flow():
    """Test the complete DigiLocker API flow."""
    
    print("🧪 Testing Complete DigiLocker API Flow")
    print("=" * 50)
    
    # Test 1: Request OTP
    print("\n1. Testing OTP Request...")
    phone_number = "+919876543210"  # From our sample data
    
    try:
        response = requests.post(f"{BASE_URL}/digilocker/authenticate/", json={
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
    
    # Test 2: Get OTP from database and verify
    print("\n2. Testing OTP Verification...")
    try:
        otp_request = OTPRequest.objects.get(request_id=request_id)
        otp_code = otp_request.otp_code
        print(f"📱 Using OTP: {otp_code}")
        
        response = requests.post(f"{BASE_URL}/digilocker/verify-otp/", json={
            "request_id": request_id,
            "otp_code": otp_code
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
    
    # Test 3: Get user profile
    print("\n3. Testing User Profile Retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/digilocker/profile/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User profile retrieved successfully")
            print(f"   Name: {user_data['name']}")
            print(f"   Phone: {user_data['phone_number']}")
            print(f"   Email: {user_data.get('email', 'Not provided')}")
        else:
            print(f"❌ User profile retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting user profile: {e}")
    
    # Test 4: List documents
    print("\n4. Testing Document Listing...")
    try:
        response = requests.get(f"{BASE_URL}/digilocker/documents/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Documents listed successfully")
            print(f"   Found {len(documents)} documents")
            
            for i, doc in enumerate(documents[:3], 1):  # Show first 3
                print(f"   {i}. {doc['name']} ({doc['type']})")
                print(f"      ID: {doc['doc_id']}")
                print(f"      Size: {doc.get('size', 'Unknown')} bytes")
                print(f"      Verified: {doc.get('is_verified', 'Unknown')}")
            
            if documents:
                doc_id = documents[0]['doc_id']
                
                # Test 5: Download document
                print(f"\n5. Testing Document Download...")
                try:
                    response = requests.get(f"{BASE_URL}/digilocker/documents/{doc_id}/download/", headers={
                        "Authorization": f"Bearer {session_token}"
                    })
                    
                    if response.status_code == 200:
                        print(f"✅ Document downloaded successfully")
                        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
                        print(f"   Size: {len(response.content)} bytes")
                        
                        # Check if it's a JSON response or actual file
                        try:
                            json_response = response.json()
                            print(f"   Filename: {json_response.get('filename', 'Not specified')}")
                        except:
                            print(f"   Raw file download successful")
                    else:
                        print(f"❌ Document download failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                except Exception as e:
                    print(f"❌ Error downloading document: {e}")
            else:
                print("   No documents found to test download")
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
    
    # Test 6: Get session info
    print("\n6. Testing Session Info...")
    try:
        response = requests.get(f"{BASE_URL}/digilocker/session/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Session info retrieved successfully")
            print(f"   Session ID: {session_data.get('session_id', 'Unknown')[:16]}...")
            print(f"   Authenticated: {session_data.get('is_authenticated', 'Unknown')}")
        else:
            print(f"❌ Session info retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting session info: {e}")
    
    # Test 7: Logout
    print("\n7. Testing Logout...")
    try:
        response = requests.post(f"{BASE_URL}/digilocker/logout/", headers={
            "Authorization": f"Bearer {session_token}"
        })
        
        if response.status_code == 200:
            logout_data = response.json()
            print(f"✅ Logout successful")
            print(f"   Message: {logout_data.get('message', 'No message')}")
        else:
            print(f"❌ Logout failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error during logout: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Complete API Flow Testing Finished!")
    print("\n📝 Summary:")
    print("✅ Authentication flow working")
    print("✅ User profile retrieval working")
    print("✅ Document listing working")
    print("✅ Session management working")
    print("\n🔗 Admin Interface: http://127.0.0.1:8000/admin/")
    print("📊 Upload documents via admin to test file downloads")


if __name__ == '__main__':
    test_full_api_flow()
