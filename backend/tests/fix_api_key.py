#!/usr/bin/env python3
"""
Fix API key configuration and restart Django.
"""

import os
import subprocess
import sys

def fix_api_key():
    """Fix API key configuration."""
    
    # The working API key from our test
    working_key = "AIzaSyDWjcwj-56ZftRddoawhtA_uGQ_0q9CCf4"
    
    print("🔧 Fixing API key configuration...")
    
    # Update .env file
    env_content = f"""# Add your Gemini API key here
# Get it from https://ai.google.dev/
# IMPORTANT: Replace with your new valid API key
GEMINI_API_KEY={working_key}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Updated .env file")
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = working_key
    
    print("✅ Set environment variable")
    
    # Test the key
    print("🧪 Testing API key...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=working_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello", request_options={'timeout': 5})
        print(f"✅ API key test successful: {response.text[:30]}...")
        return True
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    if fix_api_key():
        print("\n🎉 API key configuration fixed!")
        print("📝 Next steps:")
        print("   1. Restart Django server: uv run python manage.py runserver")
        print("   2. Test chat functionality")
    else:
        print("\n🚨 API key configuration failed!")
        print("💡 You may need to get a new API key from https://ai.google.dev/")