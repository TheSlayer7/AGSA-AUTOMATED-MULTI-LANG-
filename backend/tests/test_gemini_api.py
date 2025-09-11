#!/usr/bin/env python3
"""
Simple test script to verify Gemini API functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_gemini_api():
    """Test Gemini API with current configuration."""
    
    print("🔍 Testing Gemini API...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Test with the new Google GenAI client
        print("\n📞 Testing with google.generativeai client...")
        
        import google.generativeai as genai
        
        # Configure the client
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test generation
        print("🚀 Sending test prompt...")
        response = model.generate_content("Explain how AI works in a few words")
        
        print("✅ API call successful!")
        print(f"📝 Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Check specific error types
        if "expired" in str(e).lower():
            print("💡 This appears to be an API key expiration issue")
        elif "invalid" in str(e).lower():
            print("💡 This appears to be an invalid API key issue")
        elif "quota" in str(e).lower():
            print("💡 This appears to be a quota/billing issue")
        
        return False

def test_with_new_client():
    """Test with the new google.genai client format."""
    
    print("\n🔍 Testing with new google.genai client...")
    print("=" * 50)
    
    try:
        from google import genai
        
        # The client gets the API key from the environment variable GEMINI_API_KEY
        client = genai.Client()
        
        print("🚀 Sending test prompt with new client...")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Explain how AI works in a few words"
        )
        
        print("✅ New client API call successful!")
        print(f"📝 Response: {response.text}")
        return True
        
    except ImportError:
        print("⚠️  New google.genai client not available, using standard client")
        return False
    except Exception as e:
        print(f"❌ New client API call failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False

def main():
    """Run all API tests."""
    
    print("🧪 Gemini API Test Suite")
    print("=" * 50)
    
    # Test 1: Standard client
    success1 = test_gemini_api()
    
    # Test 2: New client format
    success2 = test_with_new_client()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    print(f"Standard client: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"New client:      {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 or success2:
        print("\n🎉 At least one client is working!")
        print("💡 Your API key appears to be valid")
    else:
        print("\n🚨 Both clients failed!")
        print("💡 Possible solutions:")
        print("   1. Get a new API key from https://ai.google.dev/")
        print("   2. Make sure you selected 'Gemini API' (not PaLM API)")
        print("   3. Check if billing is enabled for your Google Cloud project")
        print("   4. Test your key at https://makersuite.google.com/")

if __name__ == "__main__":
    main()