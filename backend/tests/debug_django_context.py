import os
import django

# Setup Django exactly like the runserver would
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

# Now check the service state
from chat.ai_service import gemini_service

print("=== DJANGO CONTEXT DEBUG ===")
print(f"gemini_service instance: {gemini_service}")
print(f"gemini_service.model: {gemini_service.model}")
print(f"gemini_service.model is None: {gemini_service.model is None}")

# Check the environment variable
from django.conf import settings
print(f"GEMINI_API_KEY in settings: {'GEMINI_API_KEY' in dir(settings)}")
if hasattr(settings, 'GEMINI_API_KEY'):
    print(f"GEMINI_API_KEY length: {len(settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else 0}")

# Let's also check if we can create a new instance
print("\n=== TESTING MODEL DIRECTLY ===")
from chat.ai_service import GeminiChatService
if gemini_service.model:
    try:
        response = gemini_service.model.generate_content("Test message")
        print(f"Direct model test successful: {response.text[:50]}...")
    except Exception as e:
        print(f"Direct model test failed: {e}")
else:
    print("Model is None, cannot test")
