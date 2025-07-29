#!/usr/bin/env python3
"""
Universal Driver Example - Revenium Griptape (RECOMMENDED)

This example demonstrates the Universal Driver that automatically detects
the provider based on model name and routes to the appropriate driver.

Features:
- Automatic provider detection (OpenAI, Anthropic, LiteLLM)
- Simplest integration option
- Zero configuration needed
- Full Griptape compatibility
- Comprehensive usage tracking
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)

def run_universal_example():
    """Run comprehensive Universal Driver examples."""
    
    print("=" * 60)
    print("Universal Driver - Auto-Detecting Integration")
    print("=" * 60)
    print("The easiest way to add Revenium metering to any Griptape application")
    print()
    
    # Check required environment variables
    if not os.getenv("REVENIUM_METERING_API_KEY"):
        print("❌ Error: REVENIUM_METERING_API_KEY environment variable is required")
        return False
    
    try:
        # Import after validation
        from revenium_griptape import ReveniumDriver
        from griptape.structures import Agent
        
        examples_run = 0
        
        # Example 1: OpenAI (if available)
        if os.getenv("OPENAI_API_KEY"):
            print("\n🤖 Example 1: OpenAI Auto-Detection")
            print("=" * 40)
            
            # Simple metadata for OpenAI example
            metadata = {
                "organization_id": "demo-universal-openai",
                "subscriber": {
                    "id": "demo-user",
                    "email": "demo@universal-openai.com",
                    "credential": {
                        "name": "openai_universal_key",
                        "value": "openai_universal_value"
                    }
                },
                "task_type": "universal_openai_example",
                "product_id": "griptape-demo"
            }
            
            print("Creating Universal Driver for OpenAI...")
            print(f"Model: gpt-3.5-turbo (auto-detects as OpenAI)")
            print(f"Organization ID: '{metadata['organization_id']}'")
            
            # Universal driver automatically detects OpenAI from model name
            driver = ReveniumDriver(
                model="gpt-3.5-turbo",  # Auto-detects as OpenAI
                usage_metadata=metadata,
                temperature=0.7
            )
            
            print(f"✅ Auto-detected provider: {driver.provider}")
            
            agent = Agent(prompt_driver=driver)
            result = agent.run("Say 'Hello from Universal Driver!'")
            print(f"Response: {result.output.value}")
            
            examples_run += 1
        
        # Example 2: Anthropic (if available)
        if os.getenv("ANTHROPIC_API_KEY"):
            print("\nExample 2: Anthropic Auto-Detection")
            print("=" * 40)
            
            # Simple metadata for Anthropic example
            metadata = {
                "organization_id": "demo-universal-anthropic",
                "subscriber": {
                    "id": "demo-user",
                    "email": "demo@universal-anthropic.com",
                    "credential": {
                        "name": "anthropic_universal_key",
                        "value": "anthropic_universal_value"
                    }
                },
                "task_type": "universal_anthropic_example",
                "product_id": "griptape-demo"
            }
            
            print("🔧 Creating Universal Driver for Anthropic...")
            print(f"Model: claude-3-haiku-20240307 (auto-detects as Anthropic)")
            print(f"Organization ID: '{metadata['organization_id']}'")
            
            # Universal driver automatically detects Anthropic from model name
            driver = ReveniumDriver(
                model="claude-3-haiku-20240307",  # Auto-detects as Anthropic
                usage_metadata=metadata,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.7
            )
            
            print(f"✅ Auto-detected provider: {driver.provider}")
            
            agent = Agent(prompt_driver=driver)
            result = agent.run("Analyze the benefits of AI usage tracking in 2 sentences.")
            print(f"Response: {result.output.value}")
            
            examples_run += 1
        
        # Example 3: LiteLLM fallback
        print("\nExample 3: LiteLLM Auto-Detection")
        print("=" * 40)
        
        metadata = {
            "organization_id": "demo-universal-litellm",
            "subscriber": {
                "id": "demo-user",
                "email": "demo@universal-litellm.com",
                "credential": {
                    "name": "litellm_universal_key",
                    "value": "litellm_universal_value"
                }
            },
            "task_type": "universal_litellm_example",
            "product_id": "griptape-demo"
        }
        
        print("Creating Universal Driver for LiteLLM...")
        print(f"Model: gemini-pro (auto-detects as LiteLLM)")
        print(f"Organization ID: '{metadata['organization_id']}'")
        print("Note: This will use LiteLLM as fallback (may require additional API keys)")
        
        # Universal driver falls back to LiteLLM for unknown models
        driver = ReveniumDriver(
            model="gemini-pro",  # Auto-detects as LiteLLM
            usage_metadata=metadata
        )
        
        print(f"✅ Auto-detected provider: {driver.provider}")
        print("Skipping actual call (would require Gemini API key)")
        
        examples_run += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 Universal Driver Auto-Detection Summary")
        print("=" * 60)
        print(f"✅ Ran {examples_run} provider detection examples")
        print("Provider Detection Rules:")
        print("   - gpt-*, text-* → OpenAI")
        print("   - claude-3*, claude-instant* → Anthropic")
        print("   - gemini-*, google/* → LiteLLM")
        print("   - Unknown models → LiteLLM (fallback)")
        print()
        print("Benefits of Universal Driver:")
        print("   ✓ Zero configuration needed")
        print("   ✓ Automatic provider detection")
        print("   ✓ Single import for all providers")
        print("   ✓ Consistent API across providers")
        print("   ✓ Easy to switch between models")
        
        if examples_run > 0:
            print(f"\n✅ Universal Driver integration completed successfully!")
            print(f"Check your Revenium dashboard for usage data from multiple providers")
        
    except Exception as e:
        print(f"\n❌ Universal Driver example failed:")
        print(f"   Error: {e}")
        print(f"   Check your API keys and network connection")
        return False
        
    return True

def run_model_switching_example():
    """Demonstrate easy model switching with Universal Driver."""
    
    print("\n🔄 Model Switching Example")
    print("=" * 40)
    print("Demonstrating how easy it is to switch between providers")
    
    try:
        from revenium_griptape import ReveniumDriver
        from griptape.structures import Agent
        
        base_metadata = {
            "organization_id": "demo-model-switching",
            "subscriber": {
                "id": "demo-user",
                "email": "demo@model-switching.com",
                "credential": {
                    "name": "switching_api_key",
                    "value": "switching_key_value"
                }
            },
            "task_type": "model_switching_example",
            "product_id": "griptape-demo"
        }
        
        models_to_test = []
        
        # Add available models based on API keys
        if os.getenv("OPENAI_API_KEY"):
            models_to_test.append(("gpt-3.5-turbo", "OpenAI"))
        
        if os.getenv("ANTHROPIC_API_KEY"):
            models_to_test.append(("claude-3-haiku-20240307", "Anthropic"))
        
        if not models_to_test:
            print("⚠️  No API keys available for model switching demo")
            return True
        
        prompt = "In one sentence, what is your model name?"
        
        for model, expected_provider in models_to_test:
            print(f"\nTesting: {model}")
            
            # Create driver - same code works for any provider!
            driver = ReveniumDriver(
                model=model,
                usage_metadata={**base_metadata, "current_model": model},
                **({} if expected_provider != "Anthropic" else {"api_key": os.getenv("ANTHROPIC_API_KEY")})
            )
            
            print(f"   Provider: {driver.provider} (expected: {expected_provider})")
            
            agent = Agent(prompt_driver=driver)
            result = agent.run(prompt)
            print(f"   Response: {result.output.value}")
        
        print("\n✅ Model switching demo completed!")
        print("Same code works across all providers - just change the model name!")
        
    except Exception as e:
        print(f"❌ Model switching demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success1 = run_universal_example()
    success2 = run_model_switching_example()
    
    if success1 and success2:
        print("\nUniversal Driver examples completed successfully!")
        print("Next steps:")
        print("   - Check your Revenium dashboard for usage data from multiple providers")
        print("   - Use Universal Driver in your applications for maximum flexibility")
        print("   - Try specific provider examples for more control")
    else:
        print("❌ Some Universal Driver examples failed. Check the error messages above.")
        exit(1) 