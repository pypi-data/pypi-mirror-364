#!/usr/bin/env python3
"""
Anthropic Integration Example - Revenium Griptape

This example demonstrates how to integrate Revenium usage metering
with Anthropic/Claude models using the ReveniumAnthropicDriver.

Features:
- Automatic usage tracking and cost monitoring
- Rich metadata injection for analytics
- Drop-in replacement for standard Anthropic drivers
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

def run_anthropic_example():
    """Run the Anthropic integration example."""
    
    print("=" * 60)
    print("🚀 Anthropic Integration with Revenium")
    print("=" * 60)
    print("Demonstrating transparent usage metering for Claude models")
    print()
    
    # Check required environment variables
    if not os.getenv("REVENIUM_METERING_API_KEY"):
        print("❌ Error: REVENIUM_METERING_API_KEY environment variable is required")
        return False
        
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not found. Skipping Anthropic example.")
        return False
    
    try:
        # Import after validation to ensure clean error messages
        from revenium_griptape import ReveniumAnthropicDriver
        from griptape.structures import Agent
        
        # Simple metadata - replace with your own values
        metadata = {
            "organization_id": "demo-anthropic-org",  # Your organization ID
            "subscriber": {
                "id": "demo-user",                    # Current user ID
                "email": "demo@anthropic-org.com",
                "credential": {
                    "name": "anthropic_api_key",
                    "value": "anthropic_key_value"
                }
            },
            "task_type": "anthropic_example",         # Type of AI task
            "product_id": "griptape-demo"             # Your product/feature
        }
        
        print("🔧 Creating Anthropic driver with Revenium integration...")
        print(f"📊 Tracking metadata: {list(metadata.keys())}")
        print(f"🔑 Organization ID: '{metadata['organization_id']}'")
        
        # Create Revenium-enabled Anthropic driver
        driver = ReveniumAnthropicDriver(
            model="claude-3-haiku-20240307",
            usage_metadata=metadata,
            temperature=0.7,
            max_tokens=150
        )
        
        print("✅ Driver created successfully")
        
        # Create agent with the driver
        agent = Agent(prompt_driver=driver)
        
        # Run example tasks
        print("\n🧠 Running AI tasks...")
        
        # Task 1: Simple response
        result1 = agent.run("Say 'Hello from Revenium integration!'")
        print(f"📝 Response: {result1.output.value}")
        
        # Task 2: Technical explanation
        result2 = agent.run("Explain what API usage metering is in one paragraph.")
        print(f"🔧 Technical: {result2.output.value}")
        
        # Task 3: Creative task  
        result3 = agent.run("Write a haiku about data analytics.")
        print(f"🎨 Creative: {result3.output.value}")
        
        print(f"\n✅ Anthropic integration completed successfully!")
        print(f"Check your Revenium dashboard for:")
        print(f"  Organization ID: '{metadata['organization_id']}'")
        print(f"  Provider: Anthropic")
        print(f"  Usage metrics and cost tracking")
        
    except Exception as e:
        print(f"\n❌ Anthropic example failed:")
        print(f"   Error: {e}")
        print(f"  Check your API keys and network connection")
        return False
        
    return True

if __name__ == "__main__":
    success = run_anthropic_example()
    
    if success:
        print("\nAnthropic example completed successfully!")
        print("Next steps:")
        print("   - Check your Revenium dashboard for usage data")
        print("   - Try the openai_example.py for GPT integration")
        print("   - Or use universal_example.py for auto-detection")
    else:
        print("❌ Anthropic example failed. Check the error messages above.")
        exit(1) 