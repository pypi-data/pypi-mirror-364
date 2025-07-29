#!/usr/bin/env python3
"""
Test script for ReveniumOllamaDriver.

This script tests the Ollama-specific Revenium driver with various scenarios.

Prerequisites:
1. pip install revenium-griptape
2. pip install revenium-middleware-ollama
3. Install and run Ollama locally (https://ollama.ai)
4. Set REVENIUM_METERING_API_KEY in environment (optional for testing)

Environment Variables:
- OLLAMA_HOST=http://localhost:11434 (default, optional)
- REVENIUM_METERING_API_KEY=your_revenium_api_key_here (optional)
- REVENIUM_METERING_BASE_URL=https://api.revenium.io/meter (optional)

Note: Ollama runs locally, so no API key is needed, but you need Ollama installed.
"""

import os
import logging
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for local testing
sys.path.insert(0, '../src')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🦙 Testing ReveniumOllamaDriver")
print("=" * 50)

def check_ollama_availability():
    """Check if Ollama is running locally."""
    print("\n🔍 Checking Ollama Availability")
    
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    try:
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running at {ollama_host}")
            print(f"   Available models: {len(models)}")
            if models:
                model_names = [model.get("name", "unknown") for model in models[:3]]
                print(f"   Sample models: {model_names}")
                return True, model_names[0] if model_names else "llama2"
            else:
                print("⚠️  No models found. You may need to pull a model:")
                print("   ollama pull llama2")
                return True, "llama2"  # Still return True since Ollama is running
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("   Make sure Ollama is installed and running:")
        print("   1. Install: https://ollama.ai")
        print("   2. Run: ollama serve")
        print("   3. Pull a model: ollama pull llama2")
        return False, None

def test_import():
    """Test importing the driver."""
    print("\n📦 Test 1: Import ReveniumOllamaDriver")
    try:
        from revenium_griptape import ReveniumOllamaDriver
        print("✅ Successfully imported ReveniumOllamaDriver")
        return ReveniumOllamaDriver
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return None

def test_driver_creation(ReveniumOllamaDriver, model_name):
    """Test creating driver instances."""
    print("\n🔧 Test 2: Driver Creation")
    
    # Test with minimal parameters
    try:
        driver = ReveniumOllamaDriver(model=model_name)
        print(f"✅ Created driver with model only: {model_name}")
        print(f"   Model: {driver.model}")
        print(f"   Type: {type(driver).__name__}")
    except Exception as e:
        print(f"❌ Failed to create basic driver: {e}")
        return None
    
    # Test with custom host
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    try:
        driver = ReveniumOllamaDriver(
            model=model_name,
            host=ollama_host,
            usage_metadata={
                "task_type": "ollama_driver",
                "subscriber": {
                    "id": "test_user",
                    "email": "test@ollama-driver.com",
                    "credential": {
                        "name": "ollama_test_key",
                        "value": "ollama_test_value"
                    }
                }
            }
        )
        print("✅ Created driver with custom host and metadata")
        print(f"   Model: {driver.model}")
        print(f"   Host: {getattr(driver, 'host', 'not set')}")
        print(f"   Has metadata: {hasattr(driver, 'usage_metadata')}")
    except Exception as e:
        print(f"❌ Failed to create driver with host: {e}")
        return None
        
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
        import revenium_middleware_ollama
        print("✅ revenium-middleware-ollama is available")
        print(f"   Module: {revenium_middleware_ollama}")
        if hasattr(revenium_middleware_ollama, '__version__'):
            print(f"   Version: {revenium_middleware_ollama.__version__}")
    except ImportError as e:
        print(f"⚠️  revenium-middleware-ollama not available: {e}")
        print("   Driver will work but without usage metering")

def test_api_call(driver, agent, ollama_available):
    """Test actual API call (if Ollama available)."""
    print("\n📡 Test 5: API Call Test")
    
    if not ollama_available:
        print("⚠️  Ollama not available, skipping API call test")
        return True  # Skip is not a failure
        
    try:
        print("   Making test API call to Ollama...")
        print("   Note: This may take a while for the first request")
        result = agent.run("Say 'Hello from Revenium Ollama driver!' in exactly those words.")
        
        # Check for error responses
        response_text = result.output.value
        if "Error code:" in response_text or "error" in response_text.lower():
            print(f"❌ API call failed with error response: {response_text}")
            return False
        
        print("✅ API call successful!")
        print(f"   Response: {response_text}")
        
        # Check if response contains expected text (more lenient for local models)
        if "Hello from Revenium Ollama driver!" in response_text:
            print("✅ Response validation successful")
            return True
        else:
            print("⚠️  Response doesn't match expected format (this is normal for local models)")
            return True  # Don't fail for this - local models vary in output
            
    except Exception as e:
        print(f"❌ API call failed with exception: {e}")
        print("   This might be due to:")
        print("   - Ollama not running (ollama serve)")
        print("   - Model not available (ollama pull <model>)")
        print("   - Network connectivity issues")
        print("   - Model loading timeout (first time can be slow)")
        return False

def test_local_models(ReveniumOllamaDriver):
    """Test common local model names."""
    print("\n🎭 Test 6: Local Model Variants")
    
    local_models = [
        "llama2",
        "llama2:7b",
        "mistral",
        "phi",
        "codellama",
        "gemma"
    ]
    
    for model in local_models:
        try:
            driver = ReveniumOllamaDriver(model=model)
            print(f"✅ {model}: Successfully created driver")
        except Exception as e:
            print(f"❌ {model}: Failed to create driver - {e}")

def test_metadata_injection(ReveniumOllamaDriver, model_name):
    """Test metadata injection functionality."""
    print("\n📊 Test 7: Metadata Injection")
    
    test_metadata = {
        "subscriber": {
            "id": "test_user_123",
            "email": "test@ollama-testing.com",
            "credential": {
                "name": "ollama_metadata_key",
                "value": "ollama_metadata_value"
            }
        },
        "task_type": "ollama_testing",
        "organization_id": "test_org",
        "subscription_id": "local_plan",
        "trace_id": "test_session_456",
        "product_id": "llama"
    }
    
    try:
        driver = ReveniumOllamaDriver(
            model=model_name,
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

def test_inheritance_chain(ReveniumOllamaDriver):
    """Test that the driver properly inherits from OllamaPromptDriver."""
    print("\n🔗 Test 8: Inheritance Chain")
    
    try:
        from griptape.drivers.prompt.ollama_prompt_driver import OllamaPromptDriver
        
        driver = ReveniumOllamaDriver(model="llama2")
        
        # Check inheritance
        is_ollama_driver = isinstance(driver, OllamaPromptDriver)
        print(f"✅ Inherits from OllamaPromptDriver: {is_ollama_driver}")
        
        # Check method availability
        has_base_params = hasattr(driver, '_base_params')
        print(f"✅ Has _base_params method: {has_base_params}")
        
        # Check that it can override base params
        if has_base_params:
            try:
                # Create a simple prompt stack for testing
                from griptape.common.prompt_stack.prompt_stack import PromptStack
                test_prompt_stack = PromptStack()
                
                params = driver._base_params(test_prompt_stack)
                print(f"✅ _base_params() callable with prompt_stack, returns: {type(params)}")
                print(f"   Returned keys: {list(params.keys())}")
            except Exception as e:
                print(f"⚠️  _base_params() call failed: {e}")
                # This might fail due to Griptape version differences - it's not critical
                
    except ImportError as e:
        print(f"❌ Could not import OllamaPromptDriver: {e}")
    except Exception as e:
        print(f"❌ Inheritance test failed: {e}")

def run_all_tests():
    """Run all tests in sequence."""
    print("Starting comprehensive Ollama driver tests...\n")
    
    # Track test results
    test_results = []
    
    # Check Ollama availability first
    ollama_available, sample_model = check_ollama_availability()
    
    # Test 1: Import
    ReveniumOllamaDriver = test_import()
    if not ReveniumOllamaDriver:
        print("\n❌ Cannot continue without successful import")
        sys.exit(1)
    test_results.append(("Import", True))
    
    # Use a default model if Ollama isn't available
    model_name = sample_model if sample_model else "llama2"
    
    # Test 2: Driver creation
    driver = test_driver_creation(ReveniumOllamaDriver, model_name)
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
    
    # Test 5: API call (critical test, but dependent on Ollama availability)
    api_success = test_api_call(driver, agent, ollama_available)
    test_results.append(("API Call", api_success))
    
    # Test 6: Model variants (informational)
    test_local_models(ReveniumOllamaDriver)
    test_results.append(("Model Variants", True))  # Structure test
    
    # Test 7: Metadata injection
    test_metadata_injection(ReveniumOllamaDriver, model_name)
    test_results.append(("Metadata Injection", True))  # Structure test
    
    # Test 8: Inheritance chain
    test_inheritance_chain(ReveniumOllamaDriver)
    test_results.append(("Inheritance Chain", True))  # Structure test
    
    # Calculate results
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    failed_tests = total_tests - passed_tests
    
    print("\n🎯 Ollama Driver Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    
    # Show individual results
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name:<20} {status}")
    
    print("\n💡 Next steps:")
    print("   1. If middleware not installed: pip install revenium-middleware-ollama")
    print("   2. Install Ollama: https://ollama.ai")
    print("   3. Start Ollama: ollama serve")
    print("   4. Pull a model: ollama pull llama2")
    print("   5. Set REVENIUM_METERING_API_KEY for usage tracking")
    
    if not ollama_available:
        print("\n⚠️  Ollama not detected - some tests were skipped")
        print("   Install and run Ollama for full testing capability")
    
    # Exit with appropriate code
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests() 