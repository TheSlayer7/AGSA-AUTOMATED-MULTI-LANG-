"""
Quick test of the new intelligent chat system.
Tests: Intent detection + Database integration
"""

import json
import time
import urllib.request
import urllib.parse

def test_chat_with_health_query():
    """Test health scheme search - should use database now"""
    
    print("🧪 Testing New Intelligent Chat System")
    print("=" * 50)
    
    # Create session
    print("1. Creating chat session...")
    session_data = json.dumps({}).encode('utf-8')
    session_req = urllib.request.Request(
        'http://127.0.0.1:8001/api/chat/sessions/',
        data=session_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        session_response = urllib.request.urlopen(session_req)
        session_result = json.loads(session_response.read().decode('utf-8'))
        session_id = session_result['session_id']
        print(f"✅ Session created: {session_id}")
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return
    
    # Test health scheme query
    print("\n2. Testing health scheme query...")
    start_time = time.time()
    
    message_data = json.dumps({
        'session_id': session_id,
        'message': 'I need health insurance schemes for my family',
        'message_type': 'text'
    }).encode('utf-8')
    
    message_req = urllib.request.Request(
        'http://127.0.0.1:8001/api/chat/send/',
        data=message_data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        message_response = urllib.request.urlopen(message_req)
        result = json.loads(message_response.read().decode('utf-8'))
        
        response_time = (time.time() - start_time) * 1000
        
        print(f"✅ Response received in {response_time:.2f}ms")
        print(f"🔍 Full Response: {result}")
        print(f"🤖 AI Response:")
        print(f"   {result.get('content', 'No content')}")
        
        # Check if response contains database schemes
        content = result.get('content', '')
        if 'Ayushman Bharat' in content or 'PM JAY' in content:
            print("🎯 SUCCESS: Response contains real database schemes!")
        elif 'found' in content.lower() and 'scheme' in content.lower():
            print("🎯 SUCCESS: AI is searching database for schemes!")
        else:
            print("⚠️  Response might not be using database yet")
            
        print(f"\n📊 Intent Category: {result.get('intent_category', 'Unknown')}")
        print(f"📊 Confidence: {result.get('confidence_score', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Message sending failed: {e}")

if __name__ == "__main__":
    test_chat_with_health_query()
