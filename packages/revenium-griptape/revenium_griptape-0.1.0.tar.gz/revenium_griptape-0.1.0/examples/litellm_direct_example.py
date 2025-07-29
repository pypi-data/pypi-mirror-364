#!/usr/bin/env python3
"""
LiteLLM Client Integration Example - Revenium Griptape

This example demonstrates how to integrate Revenium usage metering
with LiteLLM using the direct client middleware approach.

Features:
- Direct LiteLLM client integration with Revenium metering
- Automatic usage tracking and cost monitoring
- Rich metadata injection for analytics
- Works with 100+ LLM providers via LiteLLM

Note: This uses ReveniumLiteLLMDriver in direct mode (no proxy).
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

def run_litellm_client_example():
    """Run the LiteLLM client integration example using ReveniumLiteLLMDriver."""
    
    print("=" * 60)
    print("LiteLLM Client Integration with Revenium")
    print("=" * 60)
    print("Demonstrating direct LiteLLM client middleware integration")
    print()
    
    # Check required environment variables
    if not os.getenv("REVENIUM_METERING_API_KEY"):
        print("Error: REVENIUM_METERING_API_KEY environment variable is required")
        return False
        
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found. Skipping LiteLLM example.")
        print("For LiteLLM integration, you need at least one provider API key.")
        return False
    
    try:
        # Import the unified LiteLLM driver
        from revenium_griptape import ReveniumLiteLLMDriver
        from griptape.structures import Agent
        
        # Simple metadata - replace with your own values
        metadata = {
            "organization_id": "demo-litellm-client",    # Your organization ID
            "subscriber": {
                "id": "demo-user",                       # Current user ID
                "email": "demo@litellm-client.com",
                "credential": {
                    "name": "litellm_api_key",
                    "value": "litellm_key_value"
                }
            },
            "task_type": "litellm_client_example",       # Type of AI task
            "product_id": "griptape-demo"                # Your product/feature
        }
        
        print("Creating LiteLLM driver in direct mode (no proxy)...")
        print(f"Tracking metadata: {list(metadata.keys())}")
        print(f"Organization ID: '{metadata['organization_id']}'")
        print("No proxy_url specified - using direct LiteLLM client middleware")
        
        # Create driver WITHOUT proxy_url for direct client mode
        driver = ReveniumLiteLLMDriver(
            model="gpt-3.5-turbo",
            usage_metadata=metadata,
            # No proxy_url = direct client middleware mode
            temperature=0.7,
            max_tokens=150
        )
        
        print("Driver created successfully in direct mode")
        
        # Create agent with the driver
        agent = Agent(prompt_driver=driver)
        
        # Run example tasks
        print("\nRunning AI tasks via direct LiteLLM client...")
        
        try:
            # Task 1: Simple response
            print("Task 1: Simple greeting")
            result1 = agent.run("Say 'Hello from LiteLLM client integration!'")
            print(f"   Response: {result1.output.value}")
            
            # Task 2: Analysis task  
            print("\nTask 2: Technical analysis")
            result2 = agent.run("Explain the benefits of LiteLLM in 2 sentences.")
            print(f"   Analysis: {result2.output.value}")
            
            # Task 3: Creative task
            print("\nTask 3: Creative writing")
            result3 = agent.run("Write a haiku about API integration.")
            print(f"   Creative: {result3.output.value}")
            
            print(f"\nLiteLLM client integration completed successfully!")
            print(f"Check your Revenium dashboard for:")
            print(f"   Organization ID: '{metadata['organization_id']}'")
            print(f"   Provider: LiteLLM Client (Direct)")
            print(f"   Usage metrics and cost tracking")
            
        except Exception as api_error:
            print(f"\nAPI call failed:")
            print(f"   Error: {api_error}")
            print(f"   Check your API keys and network connection")
            return False
        
    except Exception as e:
        print(f"\nLiteLLM client example failed:")
        print(f"   Error: {e}")
        print(f"   Check your API keys and dependencies")
        return False
        
    return True

def show_setup_guide():
    """Show setup guide for LiteLLM client integration."""
    
    print("\nLiteLLM Client + Revenium Setup Guide")
    print("=" * 50)
    print()
    print("1. Install required packages:")
    print("   pip install revenium-griptape")
    print("   pip install 'revenium-middleware-litellm[litellm_client]'")
    print("   pip install litellm")
    print()
    print("2. Set environment variables:")
    print("   export REVENIUM_METERING_API_KEY='your-revenium-key'")
    print("   export OPENAI_API_KEY='your-openai-key'")
    print("   # Or other provider keys: GEMINI_API_KEY, COHERE_API_KEY, etc.")
    print()
    print("3. Use ReveniumLiteLLMDriver without proxy_url for direct mode")
    print()
    print("Full docs: https://pypi.org/project/revenium-middleware-litellm/")

if __name__ == "__main__":
    success = run_litellm_client_example()
    
    if success:
        print("\nLiteLLM client example completed!")
        print("Next steps:")
        print("   - Check your Revenium dashboard for usage data")
        print("   - Try different LiteLLM providers (Gemini, Cohere, etc.)")
        print("   - Use litellm_example.py for proxy integration")
        print("   - Use universal_example.py for automatic provider detection")
    else:
        show_setup_guide()
        print("\nLiteLLM client example failed. See setup guide above.")
        exit(1) 