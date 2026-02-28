import os
import django
import sys
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

# Test the chat API directly
try:
    # First create a session
    session_response = requests.post('http://localhost:8000/api/chat/sessions/', json={})
    print(f'Session creation: {session_response.status_code}')
    
    if session_response.status_code == 201:
        session_data = session_response.json()
        session_id = session_data['session_id']
        print(f'Created session: {session_id}')
        
        # Now send a message using the correct endpoint
        message_data = {
            'session_id': session_id,
            'message': 'Hello, I need help with government services',
            'message_type': 'text'
        }
        
        message_response = requests.post(
            'http://localhost:8000/api/chat/send/',
            json=message_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f'Message response: {message_response.status_code}')
        if message_response.status_code == 201:
            messages = message_response.json()
            print(f'Messages returned: {len(messages)}')
            for msg in messages:
                msg_type = msg.get('message_type', 'unknown')
                content = msg.get('content', 'no content')[:100]
                print(f'  - {msg_type}: {content}...')
        else:
            print(f'Error response: {message_response.text}')
    else:
        print(f'Session creation failed: {session_response.text}')
        
except Exception as e:
    print(f'Error: {e}')
