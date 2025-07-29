"""
Example demonstrating Universal Revenium Drivers for Griptape framework.

This example shows how the universal drivers automatically detect providers
and enable seamless usage metering across different AI providers.
"""
import os
from griptape.structures import Agent
from griptape.tasks import PromptTask
from revenium_griptape.drivers import ReveniumDriver, ReveniumEmbeddingDriver

def main():
    """Demonstrate universal drivers with auto-detection and metering."""
    
    # Common metadata for all operations
    common_metadata = {
        "trace_id": "universal-demo-456",
        "task_type": "multi-provider-analysis",
        "subscriber": {
            "id": "demo-user-789",
            "email": "demo@company.com",
            "credential": {
                "name": "universal_api_key",
                "value": "universal_key_value"
            }
        },
        "organization_id": "org-789",
        "agent": "universal-analyzer-v2"
    }
    
    print("Demonstrating Universal Revenium Drivers")
    print("=" * 60)
    
    # 1. Auto-detect OpenAI from model name for chat
    print("\nAuto-detecting OpenAI Chat Provider from model name...")
    chat_driver = ReveniumDriver(
        model="gpt-4o-mini",  # Auto-detects OpenAI
        usage_metadata=common_metadata
    )
    print(f"Detected: {chat_driver.provider} | Driver: {chat_driver}")
    
    # 2. Auto-detect OpenAI from model name for embeddings
    print("\nAuto-detecting OpenAI Embedding Provider from model name...")
    embedding_driver = ReveniumEmbeddingDriver(
        model="text-embedding-3-large",  # Auto-detects OpenAI
        usage_metadata={
            **common_metadata,
            "operation_type": "semantic_search"
        }
    )
    print(f"Detected: {embedding_driver.provider} | Driver: {embedding_driver}")
    
    # 3. Test different model patterns for auto-detection
    print("\nTesting Auto-Detection Patterns...")
    test_models = [
        ("claude-3-sonnet-20240229", "Chat"),
        ("voyage-large-2", "Embedding"),
        ("llama2:7b", "Chat"),
        ("embed-english-v3.0", "Embedding"),
        ("gemini-pro", "Chat"),
        ("nomic-embed-text", "Embedding")
    ]
    
    for model, driver_type in test_models:
        try:
            if driver_type == "Chat":
                test_driver = ReveniumDriver(model=model, usage_metadata={"test": True})
                provider = test_driver.provider
            else:
                test_driver = ReveniumEmbeddingDriver(model=model, usage_metadata={"test": True})
                provider = test_driver.provider
            print(f"  {model:<25} → {provider:<12} ({driver_type})")
        except Exception as e:
            print(f"  {model:<25} → Error: {str(e)[:30]}...")
    
    # 4. Demonstrate actual usage with auto-metering
    print("\nGenerating content with auto-detected chat driver...")
    agent = Agent(prompt_driver=chat_driver)
    content_result = agent.run(
        "Write a brief explanation of how auto-detection works in software systems."
    )
    
    generated_content = content_result.output.value
    print(f"Generated content: {generated_content[:150]}...")
    
    # 5. Create embeddings with auto-detected embedding driver
    print("\nCreating embeddings with auto-detected embedding driver...")
    embeddings = embedding_driver.embed(generated_content)
    
    print(f"Generated {len(embeddings)} embedding dimensions")
    print(f"First 3 embedding values: {embeddings[:3]}")
    
    # 6. Demonstrate provider wrapping of existing drivers
    print("\nDemonstrating Driver Wrapping...")
    from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
    from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver
    
    # Wrap existing drivers
    existing_chat_driver = OpenAiChatPromptDriver(model="gpt-4o-mini")
    wrapped_chat = ReveniumDriver(
        base_driver=existing_chat_driver,
        usage_metadata={"wrapped": True, "source": "existing_driver"}
    )
    print(f"Wrapped Chat Driver: {wrapped_chat.provider} | {wrapped_chat}")
    
    existing_embedding_driver = OpenAiEmbeddingDriver(model="text-embedding-3-small")
    wrapped_embedding = ReveniumEmbeddingDriver(
        base_driver=existing_embedding_driver,
        usage_metadata={"wrapped": True, "source": "existing_driver"}
    )
    print(f"Wrapped Embedding Driver: {wrapped_embedding.provider} | {wrapped_embedding}")
    
    # 7. Test wrapped drivers
    print("\nTesting wrapped drivers...")
    wrapped_agent = Agent(prompt_driver=wrapped_chat)
    wrapped_result = wrapped_agent.run("What are the benefits of driver wrapping?")
    print(f"Wrapped result: {wrapped_result.output.value[:100]}...")
    
    wrapped_embeddings = wrapped_embedding.embed("Testing wrapped embedding driver")
    print(f"Wrapped embeddings: {len(wrapped_embeddings)} dimensions")
    
    # 8. Force provider selection
    print("\nDemonstrating Force Provider Selection...")
    try:
        forced_driver = ReveniumDriver(
            model="custom-model-name",
            force_provider="openai",  # Force OpenAI even for unknown model
            usage_metadata={"forced": True}
        )
        print(f"Forced Provider: {forced_driver.provider}")
    except Exception as e:
        print(f"Forced provider error: {e}")
    
    print("\nUniversal Driver Demo Complete!")
    print("Key Benefits Demonstrated:")
    print("  • Automatic provider detection from model names")
    print("  • Seamless Revenium metering across providers")
    print("  • Ability to wrap existing drivers") 
    print("  • Force provider selection when needed")
    print("  • Unified interface for multiple AI providers")
    print("\nCheck your Revenium dashboard for metered usage data!")

if __name__ == "__main__":
    # Ensure environment variables are set
    required_vars = ["OPENAI_API_KEY", "REVENIUM_METERING_API_KEY", "REVENIUM_METERING_BASE_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        print("Please set these before running the example:")
        for var in missing_vars:
            print(f"  export {var}='your-{var.lower().replace('_', '-')}'")
        exit(1)
    
    main() 