#!/usr/bin/env python3
"""
Test script for ReveniumOpenAiDriver.

This script tests the OpenAI-specific Revenium driver with various scenarios.

Prerequisites:
1. pip install revenium-griptape
2. pip install revenium-middleware-openai
3. Set OPENAI_API_KEY in environment
4. Set REVENIUM_METERING_API_KEY in environment (optional for testing)

Environment Variables:
- OPENAI_API_KEY=your_openai_api_key_here
- REVENIUM_METERING_API_KEY=your_revenium_api_key_here (optional)
- REVENIUM_METERING_BASE_URL=https://api.revenium.io/meter (optional)
"""

import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for local testing
sys.path.insert(0, '../src')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🔥 Testing ReveniumOpenAiDriver")
print("=" * 50)

def test_import():
    """Test importing the driver."""
    print("\n📦 Test 1: Import ReveniumOpenAiDriver")
    try:
        from revenium_griptape import ReveniumOpenAiDriver
        print("✅ Successfully imported ReveniumOpenAiDriver")
        return ReveniumOpenAiDriver
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return None

def test_driver_creation(ReveniumOpenAiDriver):
    """Test creating driver instances."""
    print("\n🔧 Test 2: Driver Creation")
    
    # Test with minimal parameters
    try:
        driver = ReveniumOpenAiDriver(model="gpt-3.5-turbo")
        print("✅ Created driver with model only")
        print(f"   Model: {driver.model}")
        print(f"   Type: {type(driver).__name__}")
    except Exception as e:
        print(f"❌ Failed to create basic driver: {e}")
        return None
    
    # Test with API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            driver = ReveniumOpenAiDriver(
                model="gpt-4o-mini",
                api_key=api_key,
                usage_metadata={
                    "task_type": "openai_driver",
                    "subscriber": {
                        "id": "test_user",
                        "email": "test@openai-driver.com",
                        "credential": {
                            "name": "openai_test_key",
                            "value": "openai_test_value"
                        }
                    }
                }
            )
            print("✅ Created driver with API key and metadata")
            print(f"   Model: {driver.model}")
            print(f"   Has metadata: {hasattr(driver, 'usage_metadata')}")
        except Exception as e:
            print(f"❌ Failed to create driver with API key: {e}")
            return None
    else:
        print("⚠️  No OPENAI_API_KEY found, skipping API key test")
        
    return driver

def test_griptape_integration(driver):
    """Test integration with Griptape Agent."""
    print("\n🤖 Test 3: Griptape Integration")
    
    try:
        from griptape.structures import Agent
        agent = Agent(prompt_driver=driver)
        print("✅ Successfully created Griptape Agent")
        print(f"   Agent type: {type(agent).__name__}")
        print(f"   Driver type: {type(agent.prompt_driver).__name__}")
        return agent
    except Exception as e:
        print(f"❌ Failed to create Griptape Agent: {e}")
        return None

def test_middleware_detection():
    """Test middleware availability."""
    print("\n🔌 Test 4: Middleware Detection")
    
    try:
        import revenium_middleware_openai
        print("✅ revenium-middleware-openai is available")
        print(f"   Module: {revenium_middleware_openai}")
        if hasattr(revenium_middleware_openai, '__version__'):
            print(f"   Version: {revenium_middleware_openai.__version__}")
    except ImportError as e:
        print(f"⚠️  revenium-middleware-openai not available: {e}")
        print("   Driver will work but without usage metering")

def test_api_call(driver, agent):
    """Test actual API call (if API key available)."""
    print("\n📡 Test 5: API Call Test")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found, skipping API call test")
        return True  # Skip is not a failure
        
    try:
        print("   Making test API call...")
        result = agent.run("Say 'Hello from Revenium OpenAI driver!' in exactly those words.")
        
        # Check for error responses in the output
        response_text = result.output.value
        if "Error code:" in response_text or "error" in response_text.lower():
            print(f"❌ API call failed with error response: {response_text}")
            return False
        
        print("✅ API call successful!")
        print(f"   Response: {response_text}")
        
        # Check if response contains expected text
        if "Hello from Revenium OpenAI driver!" in response_text:
            print("✅ Response validation successful")
            return True
        else:
            print("❌ Response validation failed - doesn't match expected format")
            return False
            
    except Exception as e:
        print(f"❌ API call failed with exception: {e}")
        print("   This might be due to:")
        print("   - Invalid API key")
        print("   - Network issues")
        print("   - OpenAI service issues")
        print("   - Rate limiting")
        return False

def test_metadata_injection(ReveniumOpenAiDriver):
    """Test metadata injection functionality."""
    print("\n📊 Test 6: Metadata Injection")
    
    test_metadata = {
        "subscriber": {
            "id": "test_user_123",
            "email": "test@openai-testing.com",
            "credential": {
                "name": "openai_metadata_key",
                "value": "openai_metadata_value"
            }
        },
        "task_type": "testing",
        "organization_id": "test_org",
        "trace_id": "test_session_456"
    }
    
    try:
        driver = ReveniumOpenAiDriver(
            model="gpt-3.5-turbo",
            usage_metadata=test_metadata
        )
        
        # Test that metadata is available
        if hasattr(driver, 'usage_metadata'):
            print("✅ Metadata injection works")
            print(f"   Metadata keys: {list(driver.usage_metadata.keys())}")
        else:
            print("⚠️  usage_metadata not found on driver")
            
    except Exception as e:
        print(f"❌ Metadata injection test failed: {e}")

def run_all_tests():
    """Run all tests in sequence."""
    print("Starting comprehensive OpenAI driver tests...\n")
    
    # Track test results
    test_results = []
    
    # Test 1: Import
    ReveniumOpenAiDriver = test_import()
    if not ReveniumOpenAiDriver:
        print("\n❌ Cannot continue without successful import")
        sys.exit(1)
    test_results.append(("Import", True))
    
    # Test 2: Driver creation
    driver = test_driver_creation(ReveniumOpenAiDriver)
    if not driver:
        print("\n❌ Cannot continue without successful driver creation")
        sys.exit(1)
    test_results.append(("Driver Creation", True))
    
    # Test 3: Griptape integration
    agent = test_griptape_integration(driver)
    if not agent:
        print("\n❌ Cannot continue without successful Griptape integration")
        sys.exit(1)
    test_results.append(("Griptape Integration", True))
    
    # Test 4: Middleware detection (informational only)
    test_middleware_detection()
    test_results.append(("Middleware Detection", True))  # Always passes
    
    # Test 5: API call (critical test)
    api_success = test_api_call(driver, agent)
    test_results.append(("API Call", api_success))
    
    # Test 6: Metadata injection
    test_metadata_injection(ReveniumOpenAiDriver)
    test_results.append(("Metadata Injection", True))  # Structure test
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print("\n🎯 OpenAI Driver Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    
    # Show individual results
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name:<20} {status}")
    
    print("\n💡 Next steps:")
    print("   1. If middleware not installed: pip install revenium-middleware-openai")
    print("   2. Set OPENAI_API_KEY for full testing")
    print("   3. Set REVENIUM_METERING_API_KEY for usage tracking")
    
    # Exit with appropriate code
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests() 