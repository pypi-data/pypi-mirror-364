# Technical Overview: Revenium + Griptape Integration

## Executive Summary

This document captures critical technical insights and common pitfalls discovered during the development of universal Revenium middleware integration with Griptape. The goal was to create a "drop-in replacement" driver that adds automatic usage metering to any existing Griptape application with zero code changes.

**Key Achievement**: Successfully implemented `ReveniumDriver` as a universal wrapper that works with any Griptape prompt driver (OpenAI, Anthropic, LiteLLM, etc.) while providing automatic usage tracking via Revenium API.

## Architecture Overview

### Core Components

1. **ReveniumDriver** - Universal wrapper for any Griptape prompt driver
2. **ReveniumLiteLLMDriver** - Specialized driver for LiteLLM proxy integration
3. **Revenium Middleware** - Various middleware packages for different integration patterns

### Integration Patterns

```python
# Pattern 1: Wrap existing driver (RECOMMENDED)
existing_driver = OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=api_key)
metered_driver = ReveniumDriver(base_driver=existing_driver, usage_metadata=metadata)

# Pattern 2: Auto-detection from model name
auto_driver = ReveniumDriver(model="gpt-4o-mini", api_key=api_key, usage_metadata=metadata)

# Pattern 3: LiteLLM proxy integration
proxy_driver = ReveniumLiteLLMDriver(model="gpt-3.5-turbo", usage_metadata=metadata)
```

## Critical Technical Learnings

### 1. URL Duplication Problem (MAJOR PITFALL)

**Issue**: LiteLLM proxy integration was hitting `/chat/completions/chat/completions` URLs.

**Root Cause**:
- Environment variable: `LITELLM_PROXY_URL="https://ai.apisareproducts.com"`
- OpenAI client automatically appends `/chat/completions` to `base_url`
- Our driver was also manually adding `/chat/completions`
- Result: Duplicate endpoint paths

**Solution**:
```python
# WRONG - causes duplication
base_url = "https://ai.apisareproducts.com/chat/completions"
client = OpenAI(base_url=base_url)  # Results in /chat/completions/chat/completions

# CORRECT - strip endpoint before passing to OpenAI client
proxy_url = "https://ai.apisareproducts.com/chat/completions"
base_url = proxy_url.replace("/chat/completions", "")
client = OpenAI(base_url=base_url)  # OpenAI adds /chat/completions correctly
```

**Environment Fix**:
```bash
# Update .env to include full endpoint
LITELLM_PROXY_URL="https://ai.apisareproducts.com/chat/completions"
```

### 2. Model Name Transformation Issues

**Issue**: LiteLLM automatically strips provider prefixes from model names.

**Problem**:
- Input: `"openai/gpt-4o-mini"`
- LiteLLM transforms to: `"gpt-4o-mini"`
- Proxy expects: `"openai/gpt-4o-mini"`
- Result: 400/404 errors

**Solution**: Use direct OpenAI client for proxy calls to preserve exact model names.

### 3. Middleware Architecture Confusion

**Critical Understanding**: Different integration patterns require different middleware approaches:

#### Direct LiteLLM Client Middleware
```python
import revenium_middleware_litellm_client.middleware  # Import BEFORE litellm
import litellm

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=messages,
    usage_metadata=metadata  # Triggers Revenium middleware
)
```

#### LiteLLM Proxy Integration
- Proxy server must have Revenium middleware installed
- Client sends metadata via `x-revenium-*` headers
- Proxy extracts headers and forwards to Revenium API

### 4. Test Script Reliability Issues

**Problem**: Complex test scripts reported "success" despite clear failures.

**Common Issues**:
- Not validating actual response content
- Catching all exceptions without proper error detection
- Reporting success based on absence of exceptions rather than positive validation

**Solution**: Focused test scripts with explicit validation:
```python
# BAD - reports success even on errors
try:
    response = make_call()
    print("Success!")  # Printed even if response is error
except:
    print("Failed")

# GOOD - validates actual success
try:
    response = make_call()
    if response and hasattr(response, 'choices') and response.choices:
        print(f"Success: {response.choices[0].message.content}")
    else:
        print(f"Failed: Invalid response {response}")
except Exception as e:
    print(f"Failed: {e}")
```

## Common Pitfalls for Future Developers

### 1. Middleware Import Order
**CRITICAL**: Always import Revenium middleware BEFORE the target library:
```python
# CORRECT
import revenium_middleware_openai  # FIRST
import openai  # SECOND

# WRONG - middleware won't work
import openai
import revenium_middleware_openai  # Too late!
```

### 2. Environment Variable Confusion
```bash
# Different variables for different integration patterns
OPENAI_API_KEY=sk-...                    # For direct OpenAI calls
LITELLM_PROXY_URL=https://proxy/chat/completions  # For proxy calls
REVENIUM_METERING_API_KEY=rev_...        # For Revenium API
```

### 3. Usage Metadata vs Headers
- **Direct calls**: Use `usage_metadata` parameter
- **Proxy calls**: Use `x-revenium-*` headers
- Don't mix approaches in the same integration

### 4. Provider Detection Assumptions
The universal driver attempts auto-detection from model names:
- `gpt-*` → OpenAI
- `claude-*` → Anthropic
- `llama-*` → May vary by provider

Always verify auto-detection works for your use case or specify provider explicitly.

## Working Integration Examples

### Universal Driver (Recommended)
```python
from revenium_griptape import ReveniumDriver
from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.structures import Agent

# Wrap existing driver
existing_driver = OpenAiChatPromptDriver(model="gpt-3.5-turbo", api_key=api_key)
metered_driver = ReveniumDriver(
    base_driver=existing_driver,
    usage_metadata={
        "subscriber_id": "user-123",
        "task_type": "support",
        "organization_id": "acme"
    }
)

# Use exactly like before - zero code changes!
agent = Agent(prompt_driver=metered_driver)
result = agent.run("Your prompt here")
```

### LiteLLM Proxy Integration
```python
from revenium_griptape import ReveniumLiteLLMDriver

driver = ReveniumLiteLLMDriver(
    model="openai/gpt-3.5-turbo",  # Keep provider prefix for proxy
    usage_metadata=metadata
)
```

## Debugging Checklist

When integration fails, check:

1. **Import Order**: Middleware imported before target library?
2. **Environment Variables**: All required keys set and accessible?
3. **URL Structure**: No duplicate `/chat/completions` in URLs?
4. **Model Names**: Provider prefixes preserved where needed?
5. **Metadata Format**: Using correct approach (parameter vs headers)?
6. **Network Connectivity**: Can reach both LLM provider and Revenium API?
7. **Response Validation**: Actually checking response content, not just exception absence?

## Success Indicators

A working integration shows:
- **HTTP 200 OK** from LLM provider
- **HTTP 201 Created** to Revenium API (check logs)
- Valid response content from LLM
- Metadata visible in Revenium dashboard

## Key Files

- `src/revenium_griptape/drivers/revenium_universal_driver.py` - Universal wrapper
- `src/revenium_griptape/drivers/revenium_litellm_driver.py` - LiteLLM integration
- `examples/universal_revenium_example.py` - Working examples for all patterns

## Dependencies

- `griptape` - Core framework
- `revenium-middleware-openai` - For OpenAI integration
- `revenium-middleware-litellm-client` - For direct LiteLLM calls
- `litellm` - For multi-provider support
- `anthropic` - For Anthropic integration (optional)

## Future Considerations

1. **Error Handling**: Robust fallback when Revenium API unavailable
2. **Caching**: Avoid duplicate metering for retried calls
3. **Async Support**: Ensure compatibility with async Griptape workflows
4. **Configuration**: Runtime configuration without environment variables
5. **Testing**: Comprehensive integration tests for all provider combinations

---

*This document represents lessons learned from extensive integration work. Update as new patterns and issues are discovered.* 