"""
Universal Revenium driver for Griptape framework.

This driver auto-detects the LLM provider and wraps the appropriate
Revenium-enabled driver for seamless usage metering across all providers.

Supported Providers:
- Tier 1 (Direct): OpenAI, Anthropic, Ollama
- Tier 2 (via LiteLLM): Google/Gemini, Cohere, Azure OpenAI, Bedrock, and 100+ others
"""
import logging
from typing import Dict, Any, Optional, Union

from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.drivers.embedding.base_embedding_driver import BaseEmbeddingDriver
from griptape.common.prompt_stack.prompt_stack import PromptStack

logger = logging.getLogger(__name__)


class ReveniumDriver:
    """
    Universal Revenium driver factory and wrapper.
    
    This class automatically detects the LLM provider and creates the appropriate
    Revenium-enabled driver for seamless usage metering.
    
    Usage:
        # Auto-detect from model name
        driver = ReveniumDriver(model="gpt-4")
        
        # Or wrap an existing driver
        base_driver = OpenAiChatPromptDriver(model="gpt-4", api_key="...")
        driver = ReveniumDriver(base_driver=base_driver)
        
        # Use with Griptape Agent
        agent = Agent(prompt_driver=driver)
    """
    
    def __init__(self, 
                 model: Optional[str] = None,
                 base_driver: Optional[BasePromptDriver] = None,
                 force_provider: Optional[str] = None,
                 usage_metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Initialize the universal driver.
        
        Args:
            model: Model name to auto-detect provider (e.g., "gpt-4", "claude-3")
            base_driver: Existing Griptape driver to wrap with Revenium metering
            force_provider: Force specific provider ("openai", "anthropic", "ollama", "litellm")
            usage_metadata: Optional metadata for Revenium tracking
            **kwargs: Additional arguments passed to the underlying driver
                     - proxy_url/proxy_api_key automatically forces LiteLLM provider
        """
        self._wrapped_driver = None
        self._provider = None
        self.usage_metadata = usage_metadata or {}
        
        # Check if proxy parameters are provided - if so, force LiteLLM
        proxy_url = kwargs.get('proxy_url') or kwargs.get('LITELLM_PROXY_URL')
        if proxy_url and not force_provider:
            logger.info("Proxy configuration detected, forcing LiteLLM provider")
            force_provider = "litellm"
        
        # Determine the provider and create the appropriate driver
        if base_driver:
            self._provider = self._detect_provider_from_driver(base_driver)
            self._wrapped_driver = self._wrap_existing_driver(base_driver)
        elif model:
            self._provider = force_provider or self._detect_provider_from_model(model)
            self._wrapped_driver = self._create_driver_for_provider(self._provider, model, **kwargs)
        else:
            raise ValueError("Either 'model' or 'base_driver' must be provided")
            
        logger.info(f"Initialized Revenium driver for provider: {self._provider}")

    def _detect_provider_from_model(self, model: str) -> str:
        """
        Auto-detect provider from model name.
        
        Args:
            model: Model name
            
        Returns:
            Provider name ("openai", "anthropic", "ollama", or "litellm")
        """
        model_lower = model.lower()
        
        # OpenAI patterns
        if any(pattern in model_lower for pattern in ['gpt-', 'text-davinci', 'text-ada', 'text-babbage', 'text-curie']):
            return "openai"
            
        # Anthropic patterns (including date suffixes)
        if any(pattern in model_lower for pattern in ['claude-3', 'claude_3', 'claude-instant', 'claude_instant']):
            return "anthropic"
            
        # Ollama patterns (typically local models)
        if any(pattern in model_lower for pattern in ['llama', 'mistral', 'phi', 'gemma', 'codellama']):
            return "ollama"
            
        # Google/Gemini patterns (via LiteLLM)
        if any(pattern in model_lower for pattern in ['gemini-', 'gemini_', 'google/']):
            return "litellm"
            
        # Default to LiteLLM for unknown models
        logger.info(f"Unknown model '{model}', defaulting to LiteLLM provider")
        return "litellm"

    def _detect_provider_from_driver(self, driver: BasePromptDriver) -> str:
        """
        Auto-detect provider from driver class.
        
        Args:
            driver: Existing Griptape driver
            
        Returns:
            Provider name
        """
        driver_class = driver.__class__.__name__
        
        if "OpenAi" in driver_class or "OpenAI" in driver_class:
            return "openai"
        elif "Anthropic" in driver_class:
            return "anthropic"
        elif "Ollama" in driver_class:
            return "ollama"
        else:
            logger.info(f"Unknown driver type '{driver_class}', defaulting to LiteLLM provider")
            return "litellm"

    def _create_driver_for_provider(self, provider: str, model: str, **kwargs) -> BasePromptDriver:
        """
        Create the appropriate Revenium driver for the detected provider.
        
        Args:
            provider: Provider name
            model: Model name
            **kwargs: Additional driver arguments
            
        Returns:
            Revenium-enabled driver instance
        """
        try:
            if provider == "openai":
                from .revenium_openai_driver import ReveniumOpenAiDriver
                return ReveniumOpenAiDriver(model=model, usage_metadata=self.usage_metadata, **kwargs)
                
            elif provider == "anthropic":
                from .revenium_anthropic_driver import ReveniumAnthropicDriver
                return ReveniumAnthropicDriver(model=model, usage_metadata=self.usage_metadata, **kwargs)
                
            elif provider == "ollama":
                from .revenium_ollama_driver import ReveniumOllamaDriver
                return ReveniumOllamaDriver(model=model, usage_metadata=self.usage_metadata, **kwargs)
                
            elif provider == "litellm":
                from .revenium_litellm_driver import ReveniumLiteLLMDriver
                return ReveniumLiteLLMDriver(model=model, usage_metadata=self.usage_metadata, **kwargs)
                
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except ImportError as e:
            logger.error(f"Failed to import {provider} driver: {e}")
            raise ImportError(
                f"Could not load {provider} driver. Make sure griptape supports {provider} "
                f"and the required dependencies are installed."
            )

    def _wrap_existing_driver(self, base_driver: BasePromptDriver) -> BasePromptDriver:
        """
        Wrap an existing driver with Revenium metering.
        
        Args:
            base_driver: Existing Griptape driver
            
        Returns:
            Revenium-enabled driver
        """
        provider = self._detect_provider_from_driver(base_driver)
        
        try:
            if provider == "openai":
                from .revenium_openai_driver import ReveniumOpenAiDriver
                # Extract parameters from base driver
                wrapped = ReveniumOpenAiDriver(
                    model=base_driver.model,
                    api_key=getattr(base_driver, 'api_key', None),
                    temperature=getattr(base_driver, 'temperature', 0.1),
                    max_tokens=getattr(base_driver, 'max_tokens', None),
                    usage_metadata=self.usage_metadata
                )
                return wrapped
                
            elif provider == "anthropic":
                from .revenium_anthropic_driver import ReveniumAnthropicDriver
                wrapped = ReveniumAnthropicDriver(
                    model=base_driver.model,
                    api_key=getattr(base_driver, 'api_key', None),
                    temperature=getattr(base_driver, 'temperature', 0.1),
                    max_tokens=getattr(base_driver, 'max_tokens', None),
                    usage_metadata=self.usage_metadata
                )
                return wrapped
                
            elif provider == "ollama":
                from .revenium_ollama_driver import ReveniumOllamaDriver
                wrapped = ReveniumOllamaDriver(
                    model=base_driver.model,
                    host=getattr(base_driver, 'host', None),
                    temperature=getattr(base_driver, 'temperature', 0.1),
                    max_tokens=getattr(base_driver, 'max_tokens', None),
                    usage_metadata=self.usage_metadata
                )
                return wrapped
                
            else:
                # For unknown drivers, we can't wrap them yet
                logger.warning(f"Cannot wrap {provider} driver with Revenium metering yet")
                return base_driver
                
        except ImportError:
            logger.warning(f"Could not import {provider} driver, returning original driver")
            return base_driver

    # Delegate all method calls to the wrapped driver
    def __getattr__(self, name):
        """Delegate all method calls to the wrapped driver."""
        if self._wrapped_driver is None:
            raise AttributeError(f"No wrapped driver available")
        return getattr(self._wrapped_driver, name)
        
    def __str__(self):
        """String representation."""
        return f"ReveniumDriver({self._provider}: {self._wrapped_driver})"
        
    def __repr__(self):
        """String representation."""
        return self.__str__()

    @property 
    def provider(self) -> str:
        """Get the detected provider name."""
        return self._provider
        
    @property
    def wrapped_driver(self) -> BasePromptDriver:
        """Get the underlying wrapped driver."""
        return self._wrapped_driver


class ReveniumEmbeddingDriver:
    """
    Universal Revenium embedding driver factory and wrapper.
    
    This class automatically detects the embedding provider and creates the appropriate
    Revenium-enabled embedding driver for seamless usage metering.
    
    Usage:
        # Auto-detect from model name
        driver = ReveniumEmbeddingDriver(model="text-embedding-3-large")
        
        # Or wrap an existing embedding driver
        base_driver = OpenAiEmbeddingDriver(model="text-embedding-3-large")
        driver = ReveniumEmbeddingDriver(base_driver=base_driver)
        
        # Use with Griptape structures
        embeddings = driver.embed("Hello world!")
    """
    
    def __init__(self, 
                 model: Optional[str] = None,
                 base_driver: Optional[BaseEmbeddingDriver] = None,
                 force_provider: Optional[str] = None,
                 usage_metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Initialize the universal embedding driver.
        
        Args:
            model: Embedding model name to auto-detect provider (e.g., "text-embedding-3-large")
            base_driver: Existing Griptape embedding driver to wrap with Revenium metering
            force_provider: Force specific provider ("openai", "voyageai", "cohere", etc.)
            usage_metadata: Optional metadata for Revenium tracking
            **kwargs: Additional arguments passed to the underlying driver
        """
        self._wrapped_driver = None
        self._provider = None
        self.usage_metadata = usage_metadata or {}
        
        # Determine the provider and create the appropriate driver
        if base_driver:
            self._provider = self._detect_provider_from_embedding_driver(base_driver)
            self._wrapped_driver = self._wrap_existing_embedding_driver(base_driver)
        elif model:
            self._provider = force_provider or self._detect_provider_from_embedding_model(model)
            self._wrapped_driver = self._create_embedding_driver_for_provider(self._provider, model, **kwargs)
        else:
            raise ValueError("Either 'model' or 'base_driver' must be provided")
            
        logger.info(f"Initialized Revenium embedding driver for provider: {self._provider}")

    def _detect_provider_from_embedding_model(self, model: str) -> str:
        """
        Auto-detect provider from embedding model name.
        
        Args:
            model: Embedding model name
            
        Returns:
            Provider name
        """
        model_lower = model.lower()
        
        # OpenAI embedding patterns
        if any(pattern in model_lower for pattern in [
            'text-embedding-', 'text-ada-', 'text-similarity-', 'text-search-'
        ]):
            return "openai"
            
        # VoyageAI patterns
        if any(pattern in model_lower for pattern in ['voyage-', 'voyage_']):
            return "voyageai"
            
        # Cohere patterns
        if any(pattern in model_lower for pattern in ['embed-english', 'embed-multilingual']):
            return "cohere"
            
        # Hugging Face patterns
        if any(pattern in model_lower for pattern in [
            'sentence-transformers/', 'all-minilm', 'all-mpnet', 'distilbert'
        ]):
            return "huggingface"
            
        # Amazon Bedrock patterns
        if any(pattern in model_lower for pattern in ['amazon.titan-embed', 'cohere.embed']):
            return "bedrock"
            
        # Ollama patterns (local embedding models)
        if any(pattern in model_lower for pattern in ['nomic-embed', 'mxbai-embed', 'snowflake-arctic-embed']):
            return "ollama"
            
        # Default to OpenAI for unknown embedding models
        logger.info(f"Unknown embedding model '{model}', defaulting to OpenAI provider")
        return "openai"

    def _detect_provider_from_embedding_driver(self, driver: BaseEmbeddingDriver) -> str:
        """
        Auto-detect provider from embedding driver class.
        
        Args:
            driver: Existing Griptape embedding driver
            
        Returns:
            Provider name
        """
        driver_class = driver.__class__.__name__
        
        if "OpenAi" in driver_class or "OpenAI" in driver_class:
            return "openai"
        elif "VoyageAi" in driver_class or "VoyageAI" in driver_class:
            return "voyageai"
        elif "Cohere" in driver_class:
            return "cohere"
        elif "HuggingFace" in driver_class:
            return "huggingface"
        elif "Bedrock" in driver_class or "AmazonBedrock" in driver_class:
            return "bedrock"
        elif "Ollama" in driver_class:
            return "ollama"
        else:
            logger.info(f"Unknown embedding driver type '{driver_class}', defaulting to OpenAI provider")
            return "openai"

    def _create_embedding_driver_for_provider(self, provider: str, model: str, **kwargs) -> BaseEmbeddingDriver:
        """
        Create the appropriate Revenium embedding driver for the detected provider.
        
        Args:
            provider: Provider name
            model: Embedding model name
            **kwargs: Additional driver arguments
            
        Returns:
            Revenium-enabled embedding driver instance
        """
        try:
            if provider == "openai":
                from .revenium_openai_embedding_driver import ReveniumOpenAiEmbeddingDriver
                return ReveniumOpenAiEmbeddingDriver(model=model, usage_metadata=self.usage_metadata, **kwargs)
                
            elif provider == "voyageai":
                # Note: VoyageAI embedding driver would need to be created following the same pattern
                logger.warning("VoyageAI embedding driver with Revenium support not yet implemented")
                from griptape.drivers.embedding.voyageai import VoyageAiEmbeddingDriver
                return VoyageAiEmbeddingDriver(model=model, **kwargs)
                
            elif provider == "cohere":
                # Note: Cohere embedding driver would need to be created following the same pattern
                logger.warning("Cohere embedding driver with Revenium support not yet implemented")
                from griptape.drivers.embedding.cohere import CohereEmbeddingDriver
                return CohereEmbeddingDriver(model=model, **kwargs)
                
            elif provider == "huggingface":
                # Note: HuggingFace embedding driver would need to be created following the same pattern
                logger.warning("HuggingFace embedding driver with Revenium support not yet implemented")
                from griptape.drivers.embedding.huggingface_hub import HuggingFaceHubEmbeddingDriver
                return HuggingFaceHubEmbeddingDriver(model=model, **kwargs)
                
            elif provider == "ollama":
                # Note: Ollama embedding driver would need to be created following the same pattern
                logger.warning("Ollama embedding driver with Revenium support not yet implemented")
                from griptape.drivers.embedding.ollama import OllamaEmbeddingDriver
                return OllamaEmbeddingDriver(model=model, **kwargs)
                
            else:
                raise ValueError(f"Unknown embedding provider: {provider}")
                
        except ImportError as e:
            logger.error(f"Failed to import {provider} embedding driver: {e}")
            raise ImportError(
                f"Could not load {provider} embedding driver. Make sure griptape supports {provider} "
                f"and the required dependencies are installed."
            )

    def _wrap_existing_embedding_driver(self, base_driver: BaseEmbeddingDriver) -> BaseEmbeddingDriver:
        """
        Wrap an existing embedding driver with Revenium metering.
        
        Args:
            base_driver: Existing Griptape embedding driver
            
        Returns:
            Revenium-enabled embedding driver
        """
        provider = self._detect_provider_from_embedding_driver(base_driver)
        
        try:
            if provider == "openai":
                from .revenium_openai_embedding_driver import ReveniumOpenAiEmbeddingDriver
                # Extract parameters from base driver
                wrapped = ReveniumOpenAiEmbeddingDriver(
                    model=base_driver.model,
                    api_key=getattr(base_driver, 'api_key', None),
                    base_url=getattr(base_driver, 'base_url', None),
                    organization=getattr(base_driver, 'organization', None),
                    usage_metadata=self.usage_metadata
                )
                return wrapped
                
            else:
                # For other providers, return original driver until Revenium support is added
                logger.warning(f"Cannot wrap {provider} embedding driver with Revenium metering yet")
                return base_driver
                
        except ImportError:
            logger.warning(f"Could not import {provider} embedding driver, returning original driver")
            return base_driver

    # Delegate all method calls to the wrapped driver
    def __getattr__(self, name):
        """Delegate all method calls to the wrapped embedding driver."""
        if self._wrapped_driver is None:
            raise AttributeError(f"No wrapped embedding driver available")
        return getattr(self._wrapped_driver, name)
        
    def __str__(self):
        """String representation."""
        return f"ReveniumEmbeddingDriver({self._provider}: {self._wrapped_driver})"
        
    def __repr__(self):
        """String representation."""
        return self.__str__()

    @property 
    def provider(self) -> str:
        """Get the detected provider name."""
        return self._provider
        
    @property
    def wrapped_driver(self) -> BaseEmbeddingDriver:
        """Get the underlying wrapped embedding driver."""
        return self._wrapped_driver 