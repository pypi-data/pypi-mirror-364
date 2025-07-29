# Revenium Griptape Integration Examples

This directory contains clean, production-ready examples of how to integrate Revenium usage metering with Griptape using different AI providers and approaches.

## Examples Overview

| Example File | Driver | Description |
|-------------|--------|-------------|
| `openai_example.py` | ReveniumOpenAiDriver | Direct OpenAI integration with Tier 1 middleware |
| `anthropic_example.py` | ReveniumAnthropicDriver | Direct Anthropic integration with Tier 1 middleware |
| `embedding_example.py` | ReveniumOpenAiEmbeddingDriver | OpenAI embeddings integration example |
| `litellm_direct_example.py` | ReveniumLiteLLMDriver | LiteLLM direct client middleware integration |
| `litellm_proxy_example.py` | ReveniumLiteLLMDriver | LiteLLM proxy integration with official Revenium approach |
| `universal_example.py` | ReveniumDriver | Universal driver with automatic provider detection |
| `universal_driver_example.py` | ReveniumDriver/ReveniumEmbeddingDriver | Universal drivers for chat and embeddings |

## Quick Start

### 1. Installation
```bash
pip install revenium-griptape
pip install python-dotenv

# Choose middleware based on your provider:
pip install revenium-middleware-openai      # For OpenAI
pip install revenium-middleware-anthropic   # For Anthropic  
pip install revenium-middleware-litellm     # For LiteLLM (100+ providers)
```

### 2. Environment Setup
Create a `.env` file in your project root:

```bash
# Required for usage metering
REVENIUM_METERING_API_KEY=your_revenium_api_key_here

# Provider API Keys (choose what you need)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# For LiteLLM providers
GEMINI_API_KEY=your_google_gemini_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# For LiteLLM Proxy (optional)
LITELLM_PROXY_URL=https://your-litellm-proxy.com/chat/completions
LITELLM_API_KEY=your_proxy_key_here
```

### 3. Run Examples
```bash
# Direct provider integrations
python openai_example.py
python anthropic_example.py
python embedding_example.py

# LiteLLM integrations
python litellm_direct_example.py      # Direct client middleware
python litellm_proxy_example.py       # Proxy integration

# Universal drivers (auto-detects provider)
python universal_example.py
python universal_driver_example.py
```

## Usage Metadata

All examples demonstrate how to inject tracking metadata using the official Revenium fields:

```python
# Simple example - replace with your actual values
metadata = {
    "organization_id": "acme-corp",    # Customer Name or ID you wish to track usage against
    "subscriber": {
        "id": "user-456",              # Current user ID
        "email": "user@acme-corp.com",
        "credential": {
            "name": "acme_api_key",
            "value": "acme_key_value"
        }
    },
    "task_type": "document_analysis",     # Type of AI operation
    "product_id": "ai-assistant-v2"       # Your product/feature
}
```

This metadata appears in your Revenium dashboard for detailed usage analytics.

## Integration Patterns

### Pattern 1: Direct Driver (Most Control)
```python
from revenium_griptape import ReveniumOpenAiDriver

driver = ReveniumOpenAiDriver(
    model="gpt-4",
    usage_metadata=metadata
)
```

### Pattern 2: Universal Driver (Easiest)
```python
from revenium_griptape import ReveniumDriver

driver = ReveniumDriver(
    model="gpt-4",  # Auto-detects OpenAI
    usage_metadata=metadata
)
```

### Pattern 3: Universal Embedding Driver
```python
from revenium_griptape import ReveniumEmbeddingDriver

driver = ReveniumEmbeddingDriver(
    model="text-embedding-3-large",  # Auto-detects OpenAI
    usage_metadata=metadata
)
```

## Recommendation

**Start with `universal_driver_example.py`** - it demonstrates both chat and embedding capabilities with automatic provider detection. You can always switch to specific drivers later if you need more control.

## Support

- Documentation: [Revenium Docs](https://docs.revenium.io)