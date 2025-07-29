#!/usr/bin/env python3
"""
Local Package Testing Script - Pre-Publication Validation

This script tests the built package locally before publishing to PyPI.
It validates:
1. Package installation from wheel
2. Import functionality 
3. Basic driver instantiation
4. Error handling
5. Documentation examples

Run this BEFORE publishing to catch any critical issues.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_package_installation():
    """Test installing the package from the built wheel."""
    print("🔧 Testing package installation from wheel...")
    
    # Find the wheel file
    wheel_files = list(Path("dist").glob("*.whl"))
    if not wheel_files:
        print("❌ No wheel file found in dist/")
        return False
    
    wheel_path = wheel_files[0]
    print(f"   Found wheel: {wheel_path}")
    
    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        
        # Create virtual environment
        success, stdout, stderr = run_command(f"python -m venv {venv_path}")
        if not success:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        
        # Determine pip path
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"
        
        # Install the wheel
        success, stdout, stderr = run_command(f"{pip_path} install {wheel_path.absolute()}")
        if not success:
            print(f"❌ Failed to install wheel: {stderr}")
            return False
        
        print("✅ Package installed successfully")
        return True

def test_basic_imports():
    """Test basic import functionality."""
    print("📦 Testing basic imports...")
    
    test_script = '''
import sys
try:
    # Test main package import
    import revenium_griptape
    print("✅ Main package import successful")
    
    # Test version
    print(f"   Version: {revenium_griptape.__version__}")
    
    # Test driver imports
    from revenium_griptape import ReveniumDriver
    print("✅ ReveniumDriver import successful")
    
    from revenium_griptape import ReveniumEmbeddingDriver
    print("✅ ReveniumEmbeddingDriver import successful")
    
    # Test specific driver imports
    from revenium_griptape import ReveniumOpenAiDriver
    print("✅ ReveniumOpenAiDriver import successful")
    
    from revenium_griptape import ReveniumAnthropicDriver
    print("✅ ReveniumAnthropicDriver import successful")
    
    from revenium_griptape import ReveniumLiteLLMDriver
    print("✅ ReveniumLiteLLMDriver import successful")
    
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
'''
    
    success, stdout, stderr = run_command(f"python -c \"{test_script}\"")
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Import test failed: {stderr}")
        return False

def test_driver_instantiation():
    """Test basic driver instantiation without API calls."""
    print("🚀 Testing driver instantiation...")
    
    test_script = '''
import sys
try:
    from revenium_griptape import ReveniumDriver
    
    # Test universal driver instantiation
    metadata = {
        "organization_id": "test-org",
        "subscriber": {
            "id": "test-user",
            "email": "test@example.com"
        },
        "task_type": "testing"
    }
    
    # This should work without API keys since we're not making calls
    try:
        driver = ReveniumDriver(
            model="gpt-3.5-turbo",
            usage_metadata=metadata
        )
        print(f"✅ Universal driver created: {driver.provider}")
    except Exception as e:
        # Expected to fail due to missing API key, but should fail gracefully
        if "api_key" in str(e).lower() or "openai" in str(e).lower():
            print("✅ Universal driver failed gracefully (expected - no API key)")
        else:
            print(f"❌ Unexpected error in universal driver: {e}")
            sys.exit(1)
    
    print("✅ Driver instantiation tests passed!")
    
except ImportError as e:
    print(f"❌ Import error in driver test: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error in driver test: {e}")
    sys.exit(1)
'''
    
    success, stdout, stderr = run_command(f"python -c \"{test_script}\"")
    if success:
        print(stdout)
        return True
    else:
        print(f"❌ Driver instantiation test failed: {stderr}")
        return False

def test_example_syntax():
    """Test that example files have valid syntax."""
    print("📝 Testing example file syntax...")
    
    example_files = list(Path("examples").glob("*.py"))
    
    for example_file in example_files:
        success, stdout, stderr = run_command(f"python -m py_compile {example_file}")
        if success:
            print(f"✅ {example_file.name} syntax valid")
        else:
            print(f"❌ {example_file.name} syntax error: {stderr}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Starting Local Package Testing")
    print("=" * 50)
    
    tests = [
        ("Package Installation", test_package_installation),
        ("Basic Imports", test_basic_imports),
        ("Driver Instantiation", test_driver_instantiation),
        ("Example Syntax", test_example_syntax),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Package is ready for publication.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Fix issues before publishing.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
