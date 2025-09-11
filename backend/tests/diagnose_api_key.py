#!/usr/bin/env python3
"""
Comprehensive API key diagnostic test.
"""

import os
from dotenv import load_dotenv

def diagnose_api_key():
    """Comprehensive API key diagnosis."""
    
    print("🔍 API Key Diagnostic Report")
    print("=" * 60)
    
    # Check different sources of API key
    print("1. Environment Sources:")
    print("-" * 30)
    
    # Direct environment variable
    env_key = os.environ.get('GEMINI_API_KEY')
    print(f"   OS Environment: {env_key[:10] + '...' + env_key[-4:] if env_key else 'Not found'}")
    
    # Load from .env file
    load_dotenv()
    dotenv_key = os.getenv('GEMINI_API_KEY')
    print(f"   .env file:      {dotenv_key[:10] + '...' + dotenv_key[-4:] if dotenv_key else 'Not found'}")
    
    # Check .env file directly
    try:
        with open('.env', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('GEMINI_API_KEY='):
                    file_key = line.split('=', 1)[1].strip()
                    print(f"   .env raw:       {file_key[:10] + '...' + file_key[-4:] if file_key else 'Empty'}")
                    break
    except FileNotFoundError:
        print("   .env raw:       File not found")
    
    # Test the actual key being used
    current_key = dotenv_key or env_key
    if current_key:
        print(f"\n2. Current Key Analysis:")
        print("-" * 30)
        print(f"   Full key: {current_key}")
        print(f"   Length:   {len(current_key)} characters")
        print(f"   Prefix:   {current_key[:6]} {'✅' if current_key.startswith('AIzaSy') else '❌'}")
        print(f"   Format:   {'✅ Valid format' if len(current_key) > 30 and current_key.startswith('AIzaSy') else '❌ Invalid format'}")
        
        # Quick API test
        print(f"\n3. API Test Results:")
        print("-" * 30)
        test_api_key(current_key)
    else:
        print(f"\n❌ No API key found in any source!")

def test_api_key(api_key):
    """Test the specific API key."""
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("   🚀 Testing API call...")
        response = model.generate_content("Hello", request_options={'timeout': 5})
        print(f"   ✅ SUCCESS: {response.text[:50]}...")
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ FAILED: {error_msg}")
        
        # Specific error analysis
        if "expired" in error_msg.lower():
            print("   💡 ISSUE: API key has expired")
            print("   🔧 SOLUTION: Get new key from https://ai.google.dev/")
        elif "invalid" in error_msg.lower():
            print("   💡 ISSUE: API key is invalid or wrong product")
            print("   🔧 SOLUTION: Ensure you selected 'Gemini API' specifically")
        elif "quota" in error_msg.lower():
            print("   💡 ISSUE: Quota exceeded or billing required")
            print("   🔧 SOLUTION: Check Google Cloud Console billing")
        elif "unauthorized" in error_msg.lower():
            print("   💡 ISSUE: API key lacks permissions")
            print("   🔧 SOLUTION: Regenerate key with proper permissions")

if __name__ == "__main__":
    diagnose_api_key()