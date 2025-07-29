# Universal Revenium Drivers for Griptape

## Overview

The Universal Revenium Drivers provide **automatic provider detection** and **seamless usage metering** for Griptape applications. They eliminate the need to manually select specific drivers while ensuring all AI operations are tracked through Revenium.

## Key Features

### **Automatic Provider Detection**
- Detects AI provider from model names (e.g., `gpt-4` → OpenAI, `claude-3` → Anthropic)
- Supports both chat completions and embeddings
- Falls back to sensible defaults for unknown models

### **Unified Interface**
- Single driver class for all providers
- Consistent metadata injection across providers
- Seamless switching between providers

### **Automatic Metering**
- All operations automatically tracked via Revenium
- Rich metadata support for detailed analytics
- Zero-code-change integration

## Quick Start

```python
from revenium_griptape.drivers import ReveniumDriver, ReveniumEmbeddingDriver

# Chat Completions - Auto-detects OpenAI
chat_driver = ReveniumDriver(
    model="gpt-4o-mini",
    usage_metadata={"trace_id": "my-session"}
)

# Embeddings - Auto-detects OpenAI  
embedding_driver = ReveniumEmbeddingDriver(
    model="text-embedding-3-large",
    usage_metadata={"trace_id": "my-session"}
)
```

## Supported Providers

### Chat Completions (`ReveniumDriver`)

| Provider | Model Patterns | Status |
|----------|----------------|--------|
| **OpenAI** | `gpt-*`, `text-davinci-*` | ✅ Full Support |
| **Anthropic** | `claude-3*`, `claude-instant*` | ✅ Full Support |
| **Ollama** | `llama*`, `mistral*`, `phi*` | ✅ Full Support |
| **LiteLLM** | `gemini-*`, `google/*`, 100+ others | ✅ Full Support |

### Embeddings (`ReveniumEmbeddingDriver`)

| Provider | Model Patterns | Status |
|----------|----------------|--------|
| **OpenAI** | `text-embedding-*`, `text-ada-*` | ✅ Full Support |
| **VoyageAI** | `voyage-*` | ⚠️ Planned |
| **Cohere** | `embed-english*`, `embed-multilingual*` | ⚠️ Planned |
| **HuggingFace** | `sentence-transformers/*` | ⚠️ Planned |
| **Ollama** | `nomic-embed*`, `mxbai-embed*` | ⚠️ Planned |

## Usage Patterns

### 1. Auto-Detection (Recommended)

```python
# Let the driver auto-detect the provider
driver = ReveniumDriver(model="gpt-4o-mini")
embedding_driver = ReveniumEmbeddingDriver(model="text-embedding-3-large")
```

### 2. Force Provider

```python
# Force a specific provider for unknown models
driver = ReveniumDriver(
    model="custom-model-name",
    force_provider="openai"
)
```

### 3. Wrap Existing Drivers

```python
from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver

# Wrap an existing driver with Revenium metering
existing_driver = OpenAiChatPromptDriver(model="gpt-4")
metered_driver = ReveniumDriver(base_driver=existing_driver)
```

### 4. Rich Metadata

```python
driver = ReveniumDriver(
    model="gpt-4o-mini",
    usage_metadata={
        "trace_id": "user-session-123",
        "task_type": "content-generation",
        "subscriber": {
            "id": "user-456",
            "email": "user@example.com",
            "credential": {
                "name": "user_api_key",
                "value": "user_key_value"
            }
        },
        "organization_id": "org-456"
    }
)
```

## Complete Example

```python
import os
from griptape.structures import Agent
from revenium_griptape.drivers import ReveniumDriver, ReveniumEmbeddingDriver

# Set up drivers with auto-detection
chat_driver = ReveniumDriver(
    model="gpt-4o-mini",  # Auto-detects OpenAI
    usage_metadata={
        "trace_id": "demo-session",
        "user_id": "user-123"
    }
)

embedding_driver = ReveniumEmbeddingDriver(
    model="text-embedding-3-large",  # Auto-detects OpenAI
    usage_metadata={
        "trace_id": "demo-session", 
        "operation": "semantic-search"
    }
)

# Use with Griptape Agent (automatically metered)
agent = Agent(prompt_driver=chat_driver)
result = agent.run("Explain quantum computing in simple terms")

# Create embeddings (automatically metered)
embeddings = embedding_driver.embed(result.value)

print(f"Generated {len(embeddings)} embedding dimensions")
print("Check your Revenium dashboard for usage analytics!")
```

## Auto-Detection Logic

### Chat Models
```python
# OpenAI patterns
"gpt-4" → openai
"gpt-3.5-turbo" → openai
"text-davinci-003" → openai

# Anthropic patterns  
"claude-3-sonnet-20240229" → anthropic
"claude-instant-1.2" → anthropic

# Ollama patterns
"llama2:7b" → ollama
"mistral:latest" → ollama

# LiteLLM fallback
"gemini-pro" → litellm
"unknown-model" → litellm
```

### Embedding Models
```python
# OpenAI patterns
"text-embedding-3-large" → openai
"text-ada-002" → openai

# VoyageAI patterns
"voyage-large-2" → voyageai

# Cohere patterns
"embed-english-v3.0" → cohere

# Default fallback
"unknown-embedding-model" → openai
```

## Environment Setup

```bash
# Required for Revenium metering
export REVENIUM_METERING_API_KEY="your-revenium-api-key"
export REVENIUM_METERING_BASE_URL="https://api.dev.hcapp.io/meter"

# Provider API keys (as needed)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key" 
```

## Migration from Specific Drivers

### Before (Specific Drivers)
```python
from revenium_griptape.drivers import ReveniumOpenAiDriver
driver = ReveniumOpenAiDriver(model="gpt-4", usage_metadata={...})
```

### After (Universal Drivers)
```python
from revenium_griptape.drivers import ReveniumDriver
driver = ReveniumDriver(model="gpt-4", usage_metadata={...})  # Auto-detects OpenAI
```

**Benefits of Migration:**
- ✅ Simpler imports
- ✅ Provider-agnostic code
- ✅ Easy to switch between models/providers
- ✅ Future-proof for new providers

## Advanced Configuration

### Proxy Support (LiteLLM)
```python
# Automatically forces LiteLLM provider
driver = ReveniumDriver(
    model="gpt-4",
    proxy_url="https://your-litellm-proxy.com",
    proxy_api_key="your-proxy-key"
)
```

### Debug Information
```python
driver = ReveniumDriver(model="claude-3-sonnet")
print(f"Detected provider: {driver.provider}")
print(f"Wrapped driver: {driver.wrapped_driver}")
```

## Error Handling

```python
try:
    driver = ReveniumDriver(model="unsupported-model")
    print(f"Using provider: {driver.provider}")
except ImportError as e:
    print(f"Provider not available: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Use Auto-Detection**: Let the drivers detect providers automatically
2. **Consistent Metadata**: Use the same trace_id across related operations
3. **Environment Variables**: Store credentials in environment variables
4. **Error Handling**: Wrap driver creation in try-catch blocks
5. **Logging**: Enable logging to see auto-detection decisions

```python
import logging
logging.basicConfig(level=logging.INFO)
# You'll see: "Detected provider: openai" messages
```

## Troubleshooting

### Provider Not Detected
- Check model name patterns in the detection logic
- Use `force_provider` parameter as fallback
- Enable debug logging to see detection decisions

### Import Errors
- Ensure Griptape supports the detected provider
- Install required dependencies for the provider
- Check that revenium middleware is available

### Metering Not Working
- Verify REVENIUM_METERING_* environment variables
- Check that metadata is being passed correctly
- Ensure revenium-middleware-openai is installed