#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the complete flow from phone registration to document management
"""
import requests
import json
import time

# Base URL for the Django backend
BASE_URL = 'http://127.0.0.1:8000/api'

class FrontendBackendTest:
    def __init__(self):
        self.session = requests.Session()
        self.phone_number = '+919876543210'
        self.request_id = None
        self.user_id = None
        self.auth_token = None
        
    def test_phone_registration(self):
        """Test phone number registration (request OTP)"""
        print("🔄 Testing phone registration...")
        
        data = {'phone_number': self.phone_number}
        response = self.session.post(f'{BASE_URL}/auth/request-otp/', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.request_id = result.get('request_id')  # Store request_id for OTP verification
            print(f"✅ Phone registration successful: {result['message']}")
            print(f"   Request ID: {self.request_id}")
            return True
        else:
            print(f"❌ Phone registration failed: {response.status_code} - {response.text}")
            return False
    
    def test_otp_verification(self):
        """Test OTP verification and user creation"""
        print("🔄 Testing OTP verification...")
        
        if not hasattr(self, 'request_id') or not self.request_id:
            print("❌ No request_id available from registration step")
            return False
        
        # Use the test OTP from our backend
        data = {
            'request_id': self.request_id,
            'otp_code': '123456'
        }
        response = self.session.post(f'{BASE_URL}/auth/verify-otp/', json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.user_id = result['user_id']
            self.auth_token = result.get('session_token')
            
            # Set session token header for subsequent requests
            if self.auth_token:
                self.session.headers.update({'X-Session-Token': self.auth_token})
            
            print(f"✅ OTP verification successful")
            print(f"   User ID: {self.user_id}")
            print(f"   Session token: {self.auth_token[:20]}..." if self.auth_token else "   No session token")
            return True
        else:
            print(f"❌ OTP verification failed: {response.status_code} - {response.text}")
            return False
    
    def test_user_profile(self):
        """Test getting user profile"""
        print("🔄 Testing user profile retrieval...")
        
        response = self.session.get(f'{BASE_URL}/auth/profile/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Profile retrieval successful")
            print(f"   Name: {result['name']}")
            print(f"   Phone: {result['phone_number']}")
            print(f"   Email: {result.get('email', 'Not set')}")
            return True
        else:
            print(f"❌ Profile retrieval failed: {response.status_code} - {response.text}")
            return False
    
    def test_document_types(self):
        """Test getting document types"""
        print("🔄 Testing document types...")
        
        response = self.session.get(f'{BASE_URL}/documents/types/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document types retrieved: {len(result['data'])} types available")
            for doc_type in result['data'][:3]:  # Show first 3
                print(f"   - {doc_type['name']}")
            return True
        else:
            print(f"❌ Document types failed: {response.status_code} - {response.text}")
            return False
    
    def test_user_documents(self):
        """Test getting user documents"""
        print("🔄 Testing user documents...")
        
        response = self.session.get(f'{BASE_URL}/documents/')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User documents retrieved: {len(result['data'])} documents found")
            for doc in result['data'][:3]:  # Show first 3
                print(f"   Document structure: {list(doc.keys())}")  # Debug: show available fields
                # Use the correct field names from our backend
                doc_name = doc.get('name', 'Unknown')
                doc_num = doc.get('doc_number', doc.get('number', 'Unknown'))
                print(f"   - {doc_name} (#{doc_num})")
            return True
        else:
            print(f"❌ User documents failed: {response.status_code} - {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Frontend-Backend Integration Tests")
        print("=" * 50)
        
        tests = [
            self.test_phone_registration,
            self.test_otp_verification,
            self.test_user_profile,
            self.test_document_types,
            self.test_user_documents
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                failed += 1
            
            print()  # Add spacing between tests
        
        print("=" * 50)
        print(f"📊 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! Frontend-Backend integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
        
        return failed == 0

if __name__ == '__main__':
    tester = FrontendBackendTest()
    tester.run_all_tests()
