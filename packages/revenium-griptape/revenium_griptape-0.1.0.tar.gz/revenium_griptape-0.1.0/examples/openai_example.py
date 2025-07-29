#!/usr/bin/env python3
"""
OpenAI Integration Example - Revenium Griptape

This example demonstrates how to integrate Revenium usage metering
with OpenAI models using the ReveniumOpenAiDriver.

Features:
- Automatic usage tracking and cost monitoring
- Rich metadata injection for analytics
- Drop-in replacement for standard OpenAI drivers
- Full Griptape compatibility
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

def run_openai_example():
    """Run the OpenAI integration example."""
    
    print("=" * 60)
    print("OpenAI Integration with Revenium")
    print("=" * 60)
    print("Demonstrating transparent usage metering for OpenAI models")
    print()
    
    # Check required environment variables
    if not os.getenv("REVENIUM_METERING_API_KEY"):
        print("Error: REVENIUM_METERING_API_KEY environment variable is required")
        return False
        
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not found. Skipping OpenAI example.")
        return False
    
    try:
        # Import after validation to ensure clean error messages
        from revenium_griptape import ReveniumOpenAiDriver
        from griptape.structures import Agent
        
        # Simple metadata - replace with your own values
        metadata = {
            "organization_id": "demo-openai-org",    # Your organization ID
            "subscriber": {
                "id": "demo-user",                   # Current user ID
                "email": "demo@openai-org.com",
                "credential": {
                    "name": "openai_api_key",
                    "value": "openai_key_value"
                }
            },
            "task_type": "openai_example",           # Type of AI task
            "product_id": "griptape-demo"            # Your product/feature
        }
        
        print("Creating OpenAI driver with Revenium integration...")
        print(f"Tracking metadata: {list(metadata.keys())}")
        print(f"Organization ID: '{metadata['organization_id']}'")
        
        # Create Revenium-enabled OpenAI driver
        driver = ReveniumOpenAiDriver(
            model="gpt-3.5-turbo",
            usage_metadata=metadata,
            temperature=0.7,
            max_tokens=150
        )
        
        print("Driver created successfully")
        
        # Create agent with the driver
        agent = Agent(prompt_driver=driver)
        
        # Run example tasks
        print("\nRunning AI tasks...")
        
        # Task 1: Simple response
        result1 = agent.run("Say 'Hello from Revenium integration!'")
        print(f"Response: {result1.output.value}")
        
        # Task 2: Analysis task
        result2 = agent.run("Analyze the benefits of AI usage tracking in 2 sentences.")
        print(f"Analysis: {result2.output.value}")
        
        # Task 3: Creative task  
        result3 = agent.run("Write a haiku about data analytics.")
        print(f"Creative: {result3.output.value}")
        
        print(f"\nOpenAI integration completed successfully!")
        print(f"Check your Revenium dashboard for:")
        print(f"   Organization ID: '{metadata['organization_id']}'")
        print(f"   Provider: OpenAI")
        print(f"   Usage metrics and cost tracking")
        
    except Exception as e:
        print(f"\nOpenAI example failed:")
        print(f"   Error: {e}")
        print(f"   Check your API keys and network connection")
        return False
        
    return True

if __name__ == "__main__":
    success = run_openai_example()
    
    if success:
        print("\nOpenAI example completed successfully!")
        print("Next steps:")
        print("   - Check your Revenium dashboard for usage data")
        print("   - Try the anthropic_example.py for Claude integration")
        print("   - Or use universal_example.py for auto-detection")
    else:
        print("OpenAI example failed. Check the error messages above.")
        exit(1) 