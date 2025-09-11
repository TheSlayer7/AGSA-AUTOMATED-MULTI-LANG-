import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from chat.ai_service import gemini_service

# Test the AI service directly
try:
    print("Testing Gemini service directly...")
    print(f"Service initialized: {gemini_service._initialized}")
    print(f"Model available before call: {gemini_service.model is not None}")
    
    test_message = "Hello, I need help with government services"
    user_context = {
        'name': 'Test User',
        'phone': '+919999999999',
        'documents': []
    }
    
    print(f"Calling analyze_user_message with: {test_message}")
    result = gemini_service.analyze_user_message(test_message, user_context)
    
    print(f"After call - Service initialized: {gemini_service._initialized}")
    print(f"After call - Model available: {gemini_service.model is not None}")
    print(f"Result: {result}")
    
    print(f"Response content: {result.get('response', 'No response')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
