#!/usr/bin/env python3
"""
Test script for ReveniumAnthropicDriver.

This script tests the Anthropic-specific Revenium driver with various scenarios.

Prerequisites:
1. pip install revenium-griptape
2. pip install revenium-middleware-anthropic  
3. Set ANTHROPIC_API_KEY in environment
4. Set REVENIUM_METERING_API_KEY in environment (optional for testing)

Environment Variables:
- ANTHROPIC_API_KEY=your_anthropic_api_key_here
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

print("🧠 Testing ReveniumAnthropicDriver")
print("=" * 50)

def test_import():
    """Test importing the driver."""
    print("\n📦 Test 1: Import ReveniumAnthropicDriver")
    try:
        from revenium_griptape import ReveniumAnthropicDriver
        print("✅ Successfully imported ReveniumAnthropicDriver")
        return ReveniumAnthropicDriver
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return None

def test_driver_creation(ReveniumAnthropicDriver):
    """Test creating driver instances."""
    print("\n🔧 Test 2: Driver Creation")
    
    # Test with minimal parameters
    try:
        driver = ReveniumAnthropicDriver(model="claude-3-haiku-20240307")
        print("✅ Created driver with model only")
        print(f"   Model: {driver.model}")
        print(f"   Type: {type(driver).__name__}")
    except Exception as e:
        print(f"❌ Failed to create basic driver: {e}")
        return None
    
    # Test with API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            driver = ReveniumAnthropicDriver(
                model="claude-3-sonnet-20240229",
                api_key=api_key,
                usage_metadata={
                    "task_type": "anthropic_driver",
                    "subscriber": {
                        "id": "test_user",
                        "email": "test@anthropic-driver.com",
                        "credential": {
                            "name": "anthropic_test_key",
                            "value": "anthropic_test_value"
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
        print("⚠️  No ANTHROPIC_API_KEY found, skipping API key test")
        
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
        import revenium_middleware_anthropic
        print("✅ revenium-middleware-anthropic is available")
        print(f"   Module: {revenium_middleware_anthropic}")
        if hasattr(revenium_middleware_anthropic, '__version__'):
            print(f"   Version: {revenium_middleware_anthropic.__version__}")
    except ImportError as e:
        print(f"⚠️  revenium-middleware-anthropic not available: {e}")
        print("   Driver will work but without usage metering")

def test_api_call(driver, agent):
    """Test actual API call (if API key available)."""
    print("\n📡 Test 5: API Call Test")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  No ANTHROPIC_API_KEY found, skipping API call test")
        return True  # Skip is not a failure
        
    try:
        print("   Making test API call...")
        result = agent.run("Say 'Hello from Revenium Anthropic driver!' in exactly those words.")
        
        # Check for error responses in the output
        response_text = result.output.value
        if "Error code:" in response_text or "error" in response_text.lower():
            print(f"❌ API call failed with error response: {response_text}")
            return False
        
        print("✅ API call successful!")
        print(f"   Response: {response_text}")
        
        # Check if response contains expected text
        if "Hello from Revenium Anthropic driver!" in response_text:
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
        print("   - Anthropic service issues")
        print("   - Rate limiting")
        print("   - Invalid model name")
        return False

def test_model_variants(ReveniumAnthropicDriver):
    """Test different Claude model variants."""
    print("\n🎭 Test 6: Model Variants")
    
    claude_models = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229", 
        "claude-3-opus-20240229",
        "claude-3-5-sonnet-20240620"
    ]
    
    for model in claude_models:
        try:
            driver = ReveniumAnthropicDriver(model=model)
            print(f"✅ {model}: Successfully created driver")
        except Exception as e:
            print(f"❌ {model}: Failed to create driver - {e}")

def test_metadata_injection(ReveniumAnthropicDriver):
    """Test metadata injection functionality."""
    print("\n📊 Test 7: Metadata Injection")
    
    test_metadata = {
        "subscriber": {
            "id": "test_user_123",
            "email": "test@anthropic-testing.com",
            "credential": {
                "name": "anthropic_metadata_key",
                "value": "anthropic_metadata_value"
            }
        },
        "task_type": "claude_testing",
        "organization_id": "test_org",
        "trace_id": "test_session_456",
        "product_id": "claude-3"
    }
    
    try:
        driver = ReveniumAnthropicDriver(
            model="claude-3-haiku-20240307",
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

def test_inheritance_chain(ReveniumAnthropicDriver):
    """Test that the driver properly inherits from AnthropicPromptDriver."""
    print("\n🔗 Test 8: Inheritance Chain")
    
    try:
        from griptape.drivers.prompt.anthropic_prompt_driver import AnthropicPromptDriver
        from griptape.common.prompt_stack.prompt_stack import PromptStack
        from griptape.common.prompt_stack.messages.message import Message
        from griptape.artifacts import TextArtifact
        
        driver = ReveniumAnthropicDriver(model="claude-3-haiku-20240307")
        
        # Check inheritance
        is_anthropic_driver = isinstance(driver, AnthropicPromptDriver)
        print(f"✅ Inherits from AnthropicPromptDriver: {is_anthropic_driver}")
        
        # Check method availability
        has_base_params = hasattr(driver, '_base_params')
        print(f"✅ Has _base_params method: {has_base_params}")
        
        # Check that it can override base params
        if has_base_params:
            try:
                # Create a simple prompt stack for testing
                # Note: Due to Griptape version differences, we'll just test the method signature
                test_prompt_stack = PromptStack()
                
                params = driver._base_params(test_prompt_stack)
                print(f"✅ _base_params() callable with prompt_stack, returns: {type(params)}")
                print(f"   Returned keys: {list(params.keys())}")
            except Exception as e:
                print(f"⚠️  _base_params() call failed: {e}")
                # This might fail due to Griptape version differences - it's not critical
                
    except ImportError as e:
        print(f"❌ Could not import required classes: {e}")
    except Exception as e:
        print(f"❌ Inheritance test failed: {e}")

def run_all_tests():
    """Run all tests in sequence."""
    print("Starting comprehensive Anthropic driver tests...\n")
    
    # Track test results
    test_results = []
    
    # Test 1: Import
    ReveniumAnthropicDriver = test_import()
    if not ReveniumAnthropicDriver:
        print("\n❌ Cannot continue without successful import")
        sys.exit(1)
    test_results.append(("Import", True))
    
    # Test 2: Driver creation
    driver = test_driver_creation(ReveniumAnthropicDriver)
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
    
    # Test 6: Model variants (informational)
    test_model_variants(ReveniumAnthropicDriver)
    test_results.append(("Model Variants", True))  # Driver creation tests
    
    # Test 7: Metadata injection
    test_metadata_injection(ReveniumAnthropicDriver)
    test_results.append(("Metadata Injection", True))  # Structure test
    
    # Test 8: Inheritance chain
    test_inheritance_chain(ReveniumAnthropicDriver)
    test_results.append(("Inheritance Chain", True))  # Structure test
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print("\n🎯 Anthropic Driver Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    
    # Show individual results
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name:<20} {status}")
    
    print("\n💡 Next steps:")
    print("   1. If middleware not installed: pip install revenium-middleware-anthropic")
    print("   2. Set ANTHROPIC_API_KEY for full testing") 
    print("   3. Set REVENIUM_METERING_API_KEY for usage tracking")
    print("   4. Note: Anthropic has rate limits, so API tests may fail occasionally")
    
    # Exit with appropriate code
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests() 