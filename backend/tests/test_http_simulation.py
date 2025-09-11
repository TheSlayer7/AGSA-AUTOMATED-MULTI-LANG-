#!/usr/bin/env python

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

# Import Django stuff
from django.core.wsgi import get_wsgi_application
from django.test import RequestFactory
from django.http import JsonResponse

# Import our app
from chat.views import SendMessageView

def test_http_simulation():
    """Simulate what happens during an HTTP request."""
    print("=== HTTP SIMULATION TEST ===")
    
    # Create a request factory
    factory = RequestFactory()
    
    # Create a POST request with JSON data
    import json
    data = {
        'session_id': 'test-session-123',
        'message': 'Hello, I need help with government services',
        'message_type': 'text'
    }
    
    request = factory.post(
        '/api/chat/send/',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Create the view instance
    view = SendMessageView()
    view.request = request
    
    # Check the AI service state right before calling the view
    from chat.ai_service import gemini_service
    print(f"Before view call - Model available: {gemini_service.model is not None}")
    
    # Call the view
    try:
        response = view.post(request)
        print(f"Response status: {response.status_code}")
        
        if hasattr(response, 'data'):
            assistant_content = response.data.get('assistant_message', {}).get('content', 'No content')
            print(f"Assistant response: {assistant_content[:100]}...")
        else:
            print(f"Response content: {response.content[:200]}...")
            
    except Exception as e:
        print(f"Exception in view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_http_simulation()
