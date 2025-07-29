"""
Revenium-enabled OpenAI driver for Griptape framework.

This driver wraps the standard Griptape OpenAI driver and adds transparent 
Revenium usage metering by leveraging the existing revenium-middleware-openai package.
"""
import logging
import os
import json
from typing import Dict, Any, Optional

from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.common.prompt_stack.prompt_stack import PromptStack
from griptape.common.prompt_stack.messages.message import Message

# Import the revenium OpenAI middleware - this automatically patches OpenAI calls
try:
    import revenium_middleware_openai
    REVENIUM_AVAILABLE = True
    logging.info("Revenium OpenAI middleware loaded - automatic metering enabled")
except ImportError:
    REVENIUM_AVAILABLE = False
    logging.warning("Revenium middleware not available - proceeding without metering")

# Set up logger
logger = logging.getLogger(__name__)

class ReveniumOpenAiDriver(OpenAiChatPromptDriver):
    """
    OpenAI ChatGPT driver with automatic Revenium usage metering.
    
    This driver extends the standard Griptape OpenAI driver to automatically
    meter AI usage via the revenium-middleware-openai package. It injects
    usage metadata into OpenAI API calls for detailed tracking and analytics.
    
    Key Features:
    - Zero-code-change integration with existing Griptape applications
    - Automatic usage metering and cost tracking via Revenium
    - Rich metadata injection for detailed analytics
    - Graceful fallback when Revenium is unavailable
    - Environment variable authentication (no auth injection into metadata)
    
    Args:
        usage_metadata: Optional metadata dictionary for Revenium tracking.
                       Common fields include trace_id, task_type, subscriber_email, etc.
                       NOTE: Do NOT include authentication credentials here.
        **kwargs: Standard OpenAI driver arguments (model, temperature, etc.)
    
    Authentication:
        Uses environment variables for authentication (recommended approach):
        - REVENIUM_METERING_API_KEY: Your Revenium API key
        - REVENIUM_METERING_BASE_URL: Revenium API base URL
    
    Example:
        ```python
        # Set up environment (recommended)
        os.environ["REVENIUM_METERING_API_KEY"] = "your_revenium_key"
        os.environ["REVENIUM_METERING_BASE_URL"] = "https://api.dev.hcapp.io/meter"
        
        driver = ReveniumOpenAiDriver(
            model="gpt-4o-mini",
            usage_metadata={
                "trace_id": "session-123", 
                "task_type": "customer-support",
                "subscriber_email": "user@example.com"
            }
        )
        
        agent = Agent(prompt_driver=driver)
        result = agent.run("User query")  # Automatically metered
        ```
    """
    
    def __init__(
        self, 
        usage_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        # Initialize parent OpenAI driver
        super().__init__(**kwargs)
        
        # Store usage metadata for injection into OpenAI calls
        # NOTE: We do NOT store auth credentials here to prevent state corruption
        self.usage_metadata = usage_metadata or {}
        
        # Add debugging for initialization
        logger.info(f"🚀 ReveniumOpenAiDriver initialized with model: {self.model}")
        logger.debug(f"🔍 GRIPTAPE DEBUG: Usage metadata = {json.dumps(self.usage_metadata, indent=2)}")
        
        # Check middleware availability
        if REVENIUM_AVAILABLE:
            logger.info("Revenium automatic metering enabled via revenium-middleware-openai")
        else:
            logger.warning("Revenium middleware not available - usage will not be metered")

    def _base_params(self, prompt_stack: PromptStack) -> Dict[str, Any]:
        """
        Override to inject Revenium usage metadata into OpenAI API calls.
        
        This method adds clean business metadata to the OpenAI API request, which the
        revenium-middleware-openai package will automatically intercept and use for
        metering calls to the Revenium platform.
        
        IMPORTANT: This method does NOT inject authentication credentials into 
        usage_metadata to prevent corruption of the middleware's authentication state.
        Authentication should be handled via environment variables.
        """
        # Get standard parameters from parent
        params = super()._base_params(prompt_stack)
        
        logger.debug(f"🔍 GRIPTAPE DEBUG: Original params from parent = {json.dumps(params, indent=2, default=str)}")
        
        # ✅ SOLUTION: Use CLEAN metadata without authentication credentials
        # This prevents corruption of the middleware's authentication state
        clean_metadata = {}
        
        # Copy only business metadata (skip auth credentials)
        for key, value in self.usage_metadata.items():
            # ✅ CRITICAL: Exclude auth credentials to prevent state corruption
            if key not in ["revenium_api_key", "revenium_api_base_url"]:
                clean_metadata[key] = value
            else:
                logger.debug(f"🔍 GRIPTAPE DEBUG: Skipping auth credential: {key} (prevents state corruption)")
        
        # Inject clean metadata if available
        if clean_metadata:
            params["usage_metadata"] = clean_metadata
            logger.debug(f"🔍 GRIPTAPE DEBUG: Injected CLEAN metadata into OpenAI call: {json.dumps(clean_metadata, indent=2)}")
        else:
            logger.debug("🔍 GRIPTAPE DEBUG: No business metadata to inject")
        
        logger.debug(f"🔍 GRIPTAPE DEBUG: Final params with clean metadata = {json.dumps(params, indent=2, default=str)}")
        
        return params
    
    def __repr__(self) -> str:
        """String representation showing Revenium enhancement."""
        return f"ReveniumOpenAiDriver(model={self.model}, revenium_enabled={REVENIUM_AVAILABLE})" 