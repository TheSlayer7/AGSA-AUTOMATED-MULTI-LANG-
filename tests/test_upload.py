#!/usr/bin/env python3
"""
Test document upload and download functionality
"""
import requests
import json
import base64

BASE_URL = "http://127.0.0.1:8000/api"

def test_upload_download():
    print("🧪 Testing Document Upload/Download...")
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    login_response = requests.post(f"{BASE_URL}/auth/login/", json={
        "phone": "9876543210",
        "otp": "123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    session_token = login_response.json()["session_token"]
    headers = {"x-session-token": session_token}
    print("✅ Authentication successful")
    
    # Step 2: Create a test file
    print("2. Creating test file...")
    test_content = "This is a test document for upload."
    test_filename = "test_document.txt"
    
    # Step 3: Upload the document
    print("3. Uploading document...")
    files = {
        'file': (test_filename, test_content, 'text/plain')
    }
    data = {
        'document_type': 'Aadhaar'
    }
    
    upload_response = requests.post(
        f"{BASE_URL}/documents/upload/",
        headers=headers,
        files=files,
        data=data
    )
    
    print(f"Upload status: {upload_response.status_code}")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 201:
        print("✅ Document uploaded successfully")
        doc_data = upload_response.json()
        doc_id = doc_data["doc_id"]
        
        # Step 4: Download the document
        print("4. Downloading document...")
        download_response = requests.get(
            f"{BASE_URL}/documents/{doc_id}/download/",
            headers=headers
        )
        
        print(f"Download status: {download_response.status_code}")
        
        if download_response.status_code == 200:
            download_data = download_response.json()
            print("✅ Document downloaded successfully")
            
            # Decode and verify content
            if 'content' in download_data:
                decoded_content = base64.b64decode(download_data['content']).decode('utf-8')
                print(f"📄 Original content: {test_content}")
                print(f"📥 Downloaded content: {decoded_content}")
                
                if decoded_content == test_content:
                    print("✅ Content verification successful!")
                else:
                    print("❌ Content mismatch!")
            else:
                print("❌ No content in download response")
        else:
            print(f"❌ Download failed: {download_response.text}")
    else:
        print(f"❌ Upload failed: {upload_response.text}")

if __name__ == "__main__":
    test_upload_download()
