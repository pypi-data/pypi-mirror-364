"""
Example demonstrating Revenium-enabled OpenAI Chat and Embedding drivers.

This example shows how both chat completions and embeddings are automatically 
metered by the revenium-middleware-openai package with rich metadata tracking.
"""
import os
from griptape.structures import Agent
from griptape.tasks import PromptTask
from revenium_griptape.drivers import ReveniumOpenAiDriver, ReveniumOpenAiEmbeddingDriver

def main():
    """Demonstrate both chat and embedding metering in a unified workflow."""
    
    # Common metadata for both operations
    common_metadata = {
        "trace_id": "griptape-demo-123",
        "task_type": "content-analysis",
        "subscriber": {
            "id": "demo-user-456",
            "email": "demo@company.com",
            "credential": {
                "name": "demo_api_key",
                "value": "demo_key_value"
            }
        },
        "organization_id": "org-456",
        "agent": "content-analyzer-v1"
    }
    
    # 1. Set up Revenium-enabled chat driver
    print("Setting up Revenium-enabled Chat Driver...")
    chat_driver = ReveniumOpenAiDriver(
        model="gpt-4o-mini",
        usage_metadata=common_metadata
    )
    
    # 2. Set up Revenium-enabled embedding driver  
    print("Setting up Revenium-enabled Embedding Driver...")
    embedding_driver = ReveniumOpenAiEmbeddingDriver(
        model="text-embedding-3-large",
        usage_metadata={
            **common_metadata,
            "operation_type": "content_embedding"  # Additional context for embeddings
        }
    )
    
    # 3. Create content using chat completion (automatically metered)
    print("\nGenerating content with Revenium-metered chat completion...")
    agent = Agent(prompt_driver=chat_driver)
    content_result = agent.run(
        "Write a brief technical summary about vector embeddings and their use cases in AI applications."
    )
    
    generated_content = content_result.output.value
    print(f"Generated content: {generated_content[:200]}...")
    
    # 4. Create embeddings from the generated content (automatically metered) 
    print("\nCreating embeddings with Revenium-metered embedding driver...")
    embeddings = embedding_driver.embed(generated_content)
    
    print(f"Generated {len(embeddings)} embedding dimensions")
    print(f"First 5 embedding values: {embeddings[:5]}")
    
    # 5. Analyze similarity with another piece of text
    print("\nAnalyzing similarity with new content...")
    comparison_text = "Machine learning models use vector representations for semantic understanding."
    comparison_embeddings = embedding_driver.embed(comparison_text)
    
    # Simple cosine similarity calculation
    import numpy as np
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    similarity = cosine_similarity(embeddings, comparison_embeddings)
    print(f"Semantic similarity score: {similarity:.4f}")
    
    # 6. Generate analysis using chat completion (automatically metered)
    print("\nGenerating analysis with metered chat completion...")
    analysis_result = agent.run(
        f"Based on a semantic similarity score of {similarity:.4f} between two texts about AI/ML, "
        f"provide a brief interpretation of what this score means."
    )
    
    print(f"Analysis: {analysis_result.output.value}")
    
    print("\nDemo complete! Check your Revenium dashboard for metered usage data.")
    print("Both chat completions and embeddings were automatically tracked with rich metadata.")

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