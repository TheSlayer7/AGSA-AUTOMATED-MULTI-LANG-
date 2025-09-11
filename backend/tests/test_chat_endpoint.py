#!/usr/bin/env python3
"""
Test the complete chat functionality with the fixed API key.
"""

import requests
import json
import time

def test_chat_endpoint():
    """Test the chat endpoint with a sample message."""
    
    url = "http://127.0.0.1:8000/api/chat/"
    
    test_messages = [
        "Hello, I need help with government schemes",
        "I'm looking for housing schemes for low income families",
        "What documents do I need for PM-KISAN scheme?"
    ]
    
    print("🧪 Testing chat endpoint with fixed API key...")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🔹 Test {i}: {message}")
        
        payload = {
            "message": message,
            "user_context": {
                "state": "Delhi",
                "income": "300000"
            }
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"📝 Response: {data.get('response', '')[:100]}...")
                print(f"🏷️  Category: {data.get('category', 'N/A')}")
                print(f"🎯 Intent: {data.get('intent', 'N/A')}")
                print(f"📊 Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"🚨 Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🎉 Chat endpoint testing completed!")

if __name__ == "__main__":
    test_chat_endpoint()