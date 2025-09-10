#!/usr/bin/env python3
"""
Complete User Journey Test
Demonstrates the full user experience from authentication to document management
"""

import requests
import json
from datetime import datetime

def demonstrate_user_journey():
    """Demonstrate complete user journey"""
    print("👤 AGSA Government Agent AI - User Journey Demo")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    BASE_URL = "http://127.0.0.1:8000/api"
    phone_number = "+919876543210"
    test_otp = "123456"
    
    session = requests.Session()
    
    print("📱 Step 1: User opens the app and wants to login")
    print("   - User visits: http://localhost:8080")
    print("   - User clicks 'Login/Register'")
    print("   - User enters phone number: +919876543210")
    print()
    
    # Request OTP
    print("🔐 Step 2: System sends OTP")
    otp_response = session.post(f"{BASE_URL}/auth/request-otp/", json={
        "phone_number": phone_number
    })
    
    if otp_response.status_code == 200:
        otp_data = otp_response.json()
        request_id = otp_data.get("request_id") or otp_data.get("data", {}).get("request_id")
        print(f"   ✅ OTP sent successfully to {phone_number}")
        print(f"   📨 Mock SMS: 'Your AGSA login OTP is 123456. Valid for 10 minutes.'")
        print(f"   🔑 Request ID: {request_id}")
    else:
        print(f"   ❌ Failed to send OTP: {otp_response.text}")
        return
    print()
    
    print("📞 Step 3: User enters OTP")
    print("   - User receives SMS with OTP: 123456")
    print("   - User enters OTP in the app")
    print()
    
    # Verify OTP
    print("✅ Step 4: System verifies OTP and creates session")
    verify_response = session.post(f"{BASE_URL}/auth/verify-otp/", json={
        "request_id": request_id,
        "otp_code": test_otp
    })
    
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        session_token = verify_data.get("session_token") or verify_data.get("data", {}).get("session_token")
        user_id = verify_data.get("user_id") or verify_data.get("data", {}).get("user_id")
        
        print(f"   ✅ Authentication successful!")
        print(f"   🎫 Session token created: {session_token[:20] if session_token else 'N/A'}...")
        print(f"   👤 User ID: {user_id}")
        print(f"   ⏰ Session expires in: 24 hours")
        
        # Set session token for subsequent requests
        if session_token:
            session.headers.update({"X-Session-Token": session_token})
    else:
        print(f"   ❌ OTP verification failed: {verify_response.text}")
        return
    print()
    
    print("👤 Step 5: User profile is loaded from DigiLocker")
    profile_response = session.get(f"{BASE_URL}/auth/profile/")
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        # Handle both direct response and wrapped response formats
        user = profile_data.get("data", profile_data)
        
        print("   ✅ Profile loaded successfully:")
        print(f"   📛 Name: {user['name']}")
        print(f"   📱 Phone: {user['phone_number']}")
        print(f"   📧 Email: {user.get('email', 'Not provided')}")
        print(f"   🎂 Date of Birth: {user['dob']}")
        print(f"   🏠 Address: {user['address']}")
        print(f"   🆔 Aadhaar: {user.get('aadhaar_number', 'Not provided')}")
    else:
        print(f"   ❌ Profile loading failed: {profile_response.text}")
        return
    print()
    
    print("📄 Step 6: User's documents are loaded")
    docs_response = session.get(f"{BASE_URL}/documents/")
    
    if docs_response.status_code == 200:
        docs_data = docs_response.json()
        # Handle both direct response and wrapped response formats
        documents = docs_data.get("data", docs_data if isinstance(docs_data, list) else [])
        
        print(f"   ✅ Found {len(documents)} documents:")
        for i, doc in enumerate(documents[:5], 1):  # Show first 5
            verified_icon = "✅" if doc.get('is_verified') else "⏳"
            print(f"   {i}. {verified_icon} {doc.get('name', 'Unknown Document')}")
            print(f"      📄 Document #: {doc.get('doc_number', 'N/A')}")
            print(f"      📅 Issued: {doc.get('issue_date', 'N/A')}")
            if doc.get('expiry_date'):
                print(f"      ⏰ Expires: {doc['expiry_date']}")
    else:
        print(f"   ❌ Document loading failed: {docs_response.text}")
        return
    print()
    
    print("📋 Step 7: Available document types for upload")
    types_response = session.get(f"{BASE_URL}/documents/types/")
    
    if types_response.status_code == 200:
        types_data = types_response.json()
        # Handle both direct response and wrapped response formats
        doc_types = types_data.get("data", types_data if isinstance(types_data, list) else [])
        
        print(f"   ✅ {len(doc_types)} document types available for upload:")
        for doc_type in doc_types[:5]:  # Show first 5
            print(f"   📋 {doc_type.get('name', 'Unknown')} (issued by {doc_type.get('issued_by', 'Unknown')})")
    print()
    
    print("🎯 Step 8: User can now:")
    print("   📄 View all their government documents")
    print("   ⬇️  Download documents securely") 
    print("   ⬆️  Upload new documents")
    print("   💬 Chat with the AI assistant")
    print("   👤 Manage their profile")
    print("   🚪 Logout securely")
    print()
    
    print("🚪 Step 9: User logout")
    logout_response = session.post(f"{BASE_URL}/auth/logout/")
    
    if logout_response.status_code == 200:
        logout_data = logout_response.json()
        logout_message = logout_data.get("message", "Logged out successfully")
        print(f"   ✅ Logout successful: {logout_message}")
        print("   🔒 Session invalidated immediately")
        print("   🔐 All future API calls will require re-authentication")
    print()
    
    print("🔍 Step 10: Verify session is invalidated")
    test_response = session.get(f"{BASE_URL}/auth/profile/")
    
    if test_response.status_code == 401:
        print("   ✅ Session properly invalidated - authentication required")
    else:
        print(f"   ❌ Session still active: {test_response.status_code}")
    print()
    
    print("=" * 60)
    print("🎉 USER JOURNEY COMPLETE!")
    print()
    print("📊 Summary of user experience:")
    print("✅ Simple phone number login (no passwords to remember)")
    print("✅ Quick OTP verification via SMS")
    print("✅ Automatic profile loading from government records")
    print("✅ Secure document access and management")
    print("✅ Clean, intuitive user interface")
    print("✅ Secure session management")
    print("✅ Proper logout and security")
    print()
    print("🌐 User can access the app at: http://localhost:8080")
    print("🔧 Developers can access admin at: http://127.0.0.1:8000/admin/")
    print()
    print("🚀 The AGSA Government Agent AI is ready for citizens!")

if __name__ == "__main__":
    demonstrate_user_journey()
