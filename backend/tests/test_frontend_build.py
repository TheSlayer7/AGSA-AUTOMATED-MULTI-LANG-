#!/usr/bin/env python3
"""
Frontend Build Test
Tests that the frontend can build successfully and KYC page imports work
"""

import os
import sys
import subprocess

def test_frontend_build():
    """Test if the frontend builds without errors"""
    print("Testing frontend build...")
    
    # Change to project directory
    project_dir = r"c:\Users\frank\Web Projects\agsa-gov-agent-ai"
    os.chdir(project_dir)
    
    try:
        # Run build
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend build successful!")
            return True
        else:
            print("❌ Frontend build failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running build: {e}")
        return False

def test_typescript_check():
    """Test TypeScript compilation"""
    print("Testing TypeScript compilation...")
    
    try:
        # Run TypeScript check
        result = subprocess.run(['npx', 'tsc', '--noEmit'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ TypeScript check passed!")
            return True
        else:
            print("❌ TypeScript errors found:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running TypeScript check: {e}")
        return False

def main():
    """Run all frontend tests"""
    print("🔍 Frontend Test Suite")
    print("=" * 50)
    
    tests = [
        test_typescript_check,
        test_frontend_build,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Frontend Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Frontend is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
