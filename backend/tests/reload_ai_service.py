#!/usr/bin/env python3
"""
Force reload the AI service with updated API key.
"""

import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

def force_reload_ai_service():
    """Force reload the AI service with the new API key."""
    
    print("🔄 Force reloading AI service...")
    
    # Import after Django setup
    from chat.ai_service import GeminiChatService
    
    # Clear any existing instances
    if hasattr(GeminiChatService, '_instance'):
        delattr(GeminiChatService, '_instance')
    
    # Create a new instance
    service = GeminiChatService()
    
    # Force re-initialization
    service._initialized = False
    service._ensure_initialized()
    
    print("✅ AI service reloaded")
    
    # Test it
    print("🧪 Testing AI service...")
    
    try:
        result = service.analyze_user_message("Hello, test the AI")
        print(f"✅ AI service test successful: {result.get('response', '')[:50]}...")
        return True
    except Exception as e:
        print(f"❌ AI service test failed: {e}")
        return False

if __name__ == "__main__":
    success = force_reload_ai_service()
    if success:
        print("\n🎉 AI service reload successful!")
    else:
        print("\n🚨 AI service reload failed!")
        print("💡 You may need to restart the Django server completely.")