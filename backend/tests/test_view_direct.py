import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from chat.views import SendMessageView
from chat.serializers import SendMessageRequestSerializer
from chat.models import ChatSession
from api.models import UserProfile
from rest_framework.test import APIRequestFactory
import uuid

# Test the SendMessageView directly
try:
    print("Testing SendMessageView directly...")
    
    # Create a test user profile
    user_profile, created = UserProfile.objects.get_or_create(
        phone_number='+919999999999',
        defaults={
            'user_id': str(uuid.uuid4()),
            'name': 'Test User',
            'is_active': True
        }
    )
    
    # Create a test session
    session = ChatSession.objects.create(
        user_profile=user_profile,
        session_id=str(uuid.uuid4()),
        title="Test Conversation"
    )
    
    print(f"Created session: {session.session_id}")
    
    # Create a mock request
    factory = APIRequestFactory()
    request_data = {
        'session_id': session.session_id,
        'message': 'Hello, I need help with government services',
        'message_type': 'text'
    }
    
    request = factory.post('/api/chat/send/', request_data, format='json')
    
    # Create view and call it
    view = SendMessageView()
    response = view.post(request)
    
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
