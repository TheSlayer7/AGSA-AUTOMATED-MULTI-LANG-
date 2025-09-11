#!/usr/bin/env python
"""
Test script to check AI service configuration and debug connection issues
"""

import os
import sys
import django

# Setup Django
sys.path.append(r'c:\Users\frank\Web Projects\agsa-gov-agent-ai\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agsa.settings')
django.setup()

from django.conf import settings
from chat.ai_service import gemini_service

print("🔍 DEBUGGING AI SERVICE CONNECTION ISSUE")
print("=" * 50)

# Check API key configuration
api_key_env = os.getenv('GEMINI_API_KEY', '')
api_key_settings = getattr(settings, 'GEMINI_API_KEY', '')

print(f"1. API Key from environment: {'✅ Set' if api_key_env else '❌ Not set'}")
print(f"2. API Key from Django settings: {'✅ Set' if api_key_settings else '❌ Not set'}")

if api_key_env:
    print(f"   Environment key length: {len(api_key_env)} characters")
if api_key_settings:
    print(f"   Settings key length: {len(api_key_settings)} characters")

# Test AI service initialization
print(f"\n3. Testing AI service initialization...")
try:
    # Force reinitialization
    gemini_service._initialized = False
    gemini_service._ensure_initialized()
    
    if gemini_service.model:
        print("✅ AI service initialized successfully")
    else:
        print("❌ AI service failed to initialize (model is None)")
        
except Exception as e:
    print(f"❌ AI service initialization error: {e}")

# Test simple message
print(f"\n4. Testing simple AI message...")
try:
    response = gemini_service.analyze_user_message("hello", {})
    print(f"✅ AI response received: {response.get('response', 'No response')[:50]}...")
    print(f"   Response category: {response.get('category', 'Unknown')}")
    
except Exception as e:
    print(f"❌ AI message test failed: {e}")
    import traceback
    traceback.print_exc()

# Check for common issues
print(f"\n5. Common Issue Checks:")
print("-" * 30)

# Check internet connectivity
try:
    import requests
    response = requests.get('https://www.google.com', timeout=5)
    print("✅ Internet connectivity: Working")
except:
    print("❌ Internet connectivity: Failed")

# Check if we're hitting API quota limits
if not api_key_env and not api_key_settings:
    print("❌ No API key found - this is likely the main issue!")
    print("   Solution: Set GEMINI_API_KEY environment variable")
elif api_key_env and len(api_key_env) < 20:
    print("❌ API key seems too short - might be invalid")
else:
    print("✅ API key appears to be properly configured")

print(f"\n6. Recommended Solutions:")
print("-" * 30)
print("• Set GEMINI_API_KEY environment variable")
print("• Verify API key is valid and active")
print("• Check Gemini API quota limits")
print("• Ensure internet connectivity")
print("• Try restarting Django server")

if __name__ == "__main__":
    pass