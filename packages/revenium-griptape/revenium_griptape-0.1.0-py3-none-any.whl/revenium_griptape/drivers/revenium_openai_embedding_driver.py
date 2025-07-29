"""
Revenium-enabled OpenAI Embedding driver for Griptape framework.

This driver wraps the standard Griptape OpenAI Embedding driver and adds transparent 
Revenium usage metering by leveraging the existing revenium-middleware-openai package.
"""
import logging
import os
import json
from typing import Dict, Any, Optional

from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver

# Import the revenium OpenAI middleware - this automatically patches OpenAI calls
try:
    import revenium_middleware_openai
    REVENIUM_AVAILABLE = True
    logging.info("Revenium OpenAI middleware loaded - automatic embedding metering enabled")
except ImportError:
    REVENIUM_AVAILABLE = False
    logging.warning("Revenium middleware not available - proceeding without metering")

logger = logging.getLogger(__name__)

class ReveniumOpenAiEmbeddingDriver(OpenAiEmbeddingDriver):
    """
    OpenAI Embedding driver with automatic Revenium usage metering.
    
    This driver extends the standard Griptape OpenAI Embedding driver to automatically
    meter AI usage via the revenium-middleware-openai package. It injects
    usage metadata into OpenAI API calls for detailed tracking and analytics.
    
    Features:
    - Zero-code-change integration with existing Griptape applications
    - Automatic usage metering and cost tracking via Revenium
    - Rich metadata injection for detailed analytics
    - Graceful fallback when Revenium is unavailable
    - Environment variable authentication
    
    Args:
        usage_metadata: Optional metadata dictionary for Revenium tracking.
                       Common fields include trace_id, task_type, subscriber_email, etc.
                       Note: Do not include authentication credentials here.
        **kwargs: Standard OpenAI embedding driver arguments (model, api_key, etc.)
    
    Authentication:
        Uses environment variables for authentication:
        - REVENIUM_METERING_API_KEY: Your Revenium API key
        - REVENIUM_METERING_BASE_URL: Revenium API base URL
    
    Example:
        ```python
        os.environ["REVENIUM_METERING_API_KEY"] = "your_revenium_key"
        os.environ["REVENIUM_METERING_BASE_URL"] = "https://api.dev.hcapp.io/meter"
        
        driver = ReveniumOpenAiEmbeddingDriver(
            model="text-embedding-3-large",
            usage_metadata={
                "trace_id": "embed-session-123", 
                "task_type": "document-indexing",
                "subscriber_email": "user@example.com"
            }
        )
        
        embeddings = driver.embed("Hello world!")
        ```
    """
    
    def __init__(
        self, 
        usage_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.usage_metadata = usage_metadata or {}
        
        logger.info(f"ReveniumOpenAiEmbeddingDriver initialized with model: {self.model}")
        logger.debug(f"Usage metadata keys: {list(self.usage_metadata.keys())}")
        
        if REVENIUM_AVAILABLE:
            logger.info("Revenium automatic embedding metering enabled")
        else:
            logger.warning("Revenium middleware not available - usage will not be metered")

    def _params(self, chunk: str) -> Dict[str, Any]:
        """
        Override to inject Revenium usage metadata into OpenAI Embedding API calls.
        
        This method adds clean business metadata to the OpenAI API request, which the
        revenium-middleware-openai package will automatically intercept and use for
        metering calls to the Revenium platform.
        
        """
        params = super()._params(chunk)
        
        logger.debug(f"Original params from parent: {json.dumps(params, indent=2, default=str)}")
        
        # Use clean metadata without authentication credentials
        clean_metadata = {}
        
        # Copy only business metadata (skip auth credentials)
        for key, value in self.usage_metadata.items():
            if key not in ["revenium_api_key", "revenium_api_base_url"]:
                clean_metadata[key] = value
            else:
                logger.debug(f"Skipping auth credential: {key}")
        
        # Inject clean metadata if available
        if clean_metadata:
            params["usage_metadata"] = clean_metadata
            logger.debug(f"Injected metadata into OpenAI embedding call: {json.dumps(clean_metadata, indent=2)}")
        else:
            logger.debug("No business metadata to inject")
        
        logger.debug(f"Final embedding params: {json.dumps(params, indent=2, default=str)}")
        
        return params
    
    def __repr__(self) -> str:
        """String representation showing Revenium enhancement."""
        return f"ReveniumOpenAiEmbeddingDriver(model={self.model}, revenium_enabled={REVENIUM_AVAILABLE})" 