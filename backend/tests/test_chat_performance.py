#!/usr/bin/env python3
"""
Test script to demonstrate chat performance logging.
This script sends a test message to the chat API and shows the detailed timing logs.
"""

import requests
import json
import time
from datetime import datetime

def test_chat_performance():
    """Test chat API performance with detailed logging."""
    
    base_url = "http://127.0.0.1:8000"
    
    # Test message
    test_message = "Hello, I need help with government schemes for small business loans"
    
    print("=" * 60)
    print("CHAT PERFORMANCE TEST")
    print("=" * 60)
    print(f"Testing message: {test_message}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    # Record start time
    start_time = time.time()
    
    try:
        # Send chat message
        print("📤 Sending chat message...")
        response = requests.post(
            f"{base_url}/api/chat/send/",
            json={
                "message": test_message,
                "message_type": "text"
            },
            headers={
                "Content-Type": "application/json"
            },
            timeout=60  # 60 second timeout
        )
        
        # Record end time
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"✅ Response received in {total_time:.2f}ms")
        print(f"🌐 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📊 RESPONSE SUMMARY:")
            print("-" * 40)
            print(f"Session ID: {data.get('session_id', 'N/A')}")
            print(f"User Message ID: {data.get('user_message', {}).get('message_id', 'N/A')}")
            print(f"AI Response Length: {len(data.get('assistant_message', {}).get('content', ''))}")
            print(f"AI Confidence: {data.get('assistant_message', {}).get('confidence_score', 'N/A')}")
            print(f"Intent Category: {data.get('assistant_message', {}).get('intent_category', 'N/A')}")
            
            print(f"\n🤖 AI Response:")
            print("-" * 40)
            print(data.get('assistant_message', {}).get('content', 'No response'))
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        print(f"⏱️ Request timed out after {total_time:.2f}ms")
        
    except Exception as e:
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        print(f"❌ Error after {total_time:.2f}ms: {e}")
    
    print("\n" + "=" * 60)
    print("Check the Django console logs for detailed timing breakdown!")
    print("Check the browser console for frontend timing logs!")
    print("=" * 60)

if __name__ == "__main__":
    test_chat_performance()
