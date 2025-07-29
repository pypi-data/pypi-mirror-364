"""
Revenium Griptape Tools

A package that provides transparent AI usage metering and cost tracking for Griptape applications.
Universal support for all LLM providers through automatic middleware detection.

Supported Providers:
- Tier 1 (Direct): OpenAI, Anthropic, Ollama  
- Tier 2 (LiteLLM): Google/Gemini, Cohere, Azure OpenAI, Bedrock, and 100+ others
"""

__version__ = "0.1.0"

# Automatically load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional - continue without it
    pass

# Primary universal drivers (recommended)
from .drivers.revenium_universal_driver import ReveniumDriver, ReveniumEmbeddingDriver

# Tier 1 specific drivers
from .drivers.revenium_openai_driver import ReveniumOpenAiDriver
from .drivers.revenium_openai_embedding_driver import ReveniumOpenAiEmbeddingDriver
from .drivers.revenium_anthropic_driver import ReveniumAnthropicDriver
from .drivers.revenium_ollama_driver import ReveniumOllamaDriver

# Tier 2 LiteLLM driver
from .drivers.revenium_litellm_driver import ReveniumLiteLLMDriver

__all__ = [
    # Primary universal drivers (recommended)
    "ReveniumDriver",
    "ReveniumEmbeddingDriver",
    
    # Tier 1 specific drivers (for advanced usage)
    "ReveniumOpenAiDriver",
    "ReveniumOpenAiEmbeddingDriver",
    "ReveniumAnthropicDriver", 
    "ReveniumOllamaDriver",
    
    # Tier 2 LiteLLM driver (for 100+ providers)
    "ReveniumLiteLLMDriver",
] 