# 🧪 Revenium Driver Testing Suite

This folder contains comprehensive test scripts for all Revenium Griptape drivers. Each driver has its own dedicated test script that validates functionality, integration, and error handling.

## 📁 Test Scripts

| Script | Driver | Description |
|--------|--------|-------------|
| `test_openai_driver.py` | ReveniumOpenAiDriver | Tests OpenAI integration with Tier 1 middleware |
| `test_anthropic_driver.py` | ReveniumAnthropicDriver | Tests Anthropic integration with Tier 1 middleware |
| `test_ollama_driver.py` | ReveniumOllamaDriver | Tests local Ollama integration with Tier 1 middleware |
| `test_litellm_driver.py` | ReveniumLiteLLMDriver | Tests LiteLLM integration for 100+ providers |
| `test_universal_driver.py` | ReveniumDriver | Tests universal auto-detection and factory functionality |
| `run_all_tests.py` | Test Runner | Runs all test scripts and provides summary |

## 🚀 Quick Start

### Run All Tests
```bash
cd testing
python run_all_tests.py
```

### Run Specific Tests
```bash
# Run only OpenAI and Universal tests
python run_all_tests.py --tests openai,universal

# Skip tests that require special setup
python run_all_tests.py --skip ollama,litellm
```

### Run Individual Tests
```bash
# Test specific driver
python test_openai_driver.py
python test_anthropic_driver.py
python test_universal_driver.py
```

## ⚙️ Environment Setup

Create a `.env` file in the project root (not in testing folder):

```bash
# Required for usage metering (optional for testing)
REVENIUM_METERING_API_KEY=your_revenium_api_key_here
REVENIUM_METERING_BASE_URL=https://api.revenium.io/meter

# Tier 1 Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OLLAMA_HOST=http://localhost:11434  # Default for local Ollama

# Tier 2 Provider API Keys (via LiteLLM)
GEMINI_API_KEY=your_google_gemini_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
AZURE_API_KEY=your_azure_openai_api_key_here
AWS_ACCESS_KEY_ID=your_aws_access_key_here        # For Bedrock
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here    # For Bedrock

# Add other provider keys as needed - see LiteLLM docs
```

## 📋 Prerequisites

### Base Requirements
```bash
pip install revenium-griptape
pip install python-dotenv
pip install requests  # For Ollama connectivity tests
```

### Middleware Packages (Install as needed)
```bash
# Tier 1 middleware (provider-specific)
pip install revenium-middleware-openai
pip install revenium-middleware-anthropic  
pip install revenium-middleware-ollama

# Tier 2 middleware (universal LiteLLM)
pip install revenium-middleware-litellm
pip install litellm
```

### Special Setup Requirements

#### Ollama (Local Models)
1. Install Ollama: https://ollama.ai
2. Start the service: `ollama serve`
3. Pull a model: `ollama pull llama2`

#### LiteLLM (100+ Providers)
- Install LiteLLM: `pip install litellm`
- Set appropriate API keys for providers you want to test
- See [LiteLLM providers](https://docs.litellm.ai/docs/providers) for complete list

## 🧪 What Each Test Does

### OpenAI Driver Tests (`test_openai_driver.py`)
- ✅ Import verification
- ✅ Driver creation with various parameters
- ✅ Griptape Agent integration
- ✅ Middleware detection
- ✅ Real API calls (if API key available)
- ✅ Metadata injection and filtering
- ✅ Inheritance chain validation

### Anthropic Driver Tests (`test_anthropic_driver.py`)
- ✅ Import verification
- ✅ Driver creation with Claude models
- ✅ Model variant testing (haiku, sonnet, opus)
- ✅ Middleware detection
- ✅ Real API calls (if API key available)
- ✅ Metadata injection and filtering
- ✅ Inheritance chain validation

### Ollama Driver Tests (`test_ollama_driver.py`)
- ✅ Ollama service availability check
- ✅ Driver creation with local models
- ✅ Model discovery from running Ollama instance
- ✅ Middleware detection
- ✅ Real API calls to local Ollama (if running)
- ✅ Metadata injection (no API key filtering needed)
- ✅ Inheritance chain validation

### LiteLLM Driver Tests (`test_litellm_driver.py`)
- ✅ Dependency checking (LiteLLM + middleware)
- ✅ Driver creation for multiple providers
- ✅ Message conversion testing
- ✅ Parameter building validation
- ✅ Real API calls (if provider keys available)
- ✅ Metadata injection and filtering
- ✅ BasePromptDriver inheritance validation

### Universal Driver Tests (`test_universal_driver.py`)
- ✅ Provider auto-detection from model names
- ✅ Tier 1 and Tier 2 driver creation
- ✅ Existing driver wrapping
- ✅ Metadata propagation to wrapped drivers
- ✅ Provider forcing for testing
- ✅ Error handling for invalid inputs
- ✅ Real API integration across providers

## 📊 Understanding Test Results

### Success Indicators
- ✅ **Green checkmarks**: Test passed successfully
- 🎯 **Summary sections**: Overall test completion
- 🚀 **Ready messages**: Component is production-ready

### Warning Indicators
- ⚠️ **Yellow warnings**: Non-critical issues (missing optional dependencies)
- 💡 **Blue info**: Helpful tips or next steps

### Error Indicators
- ❌ **Red X marks**: Test failures that need attention
- 💥 **Explosions**: Unexpected errors
- ⏰ **Clock**: Timeout issues

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```
❌ Failed to import: No module named 'revenium_griptape'
```
**Solution**: Make sure you're running from the testing folder and the package is installed.

#### Missing Middleware
```
⚠️ revenium-middleware-openai not available
```
**Solution**: Install the middleware: `pip install revenium-middleware-openai`

#### API Key Issues
```
❌ API call failed: Invalid API key
```
**Solution**: Check your `.env` file and API key validity.

#### Ollama Connection Issues
```
❌ Cannot connect to Ollama
```
**Solution**: Start Ollama service: `ollama serve`

#### LiteLLM Missing
```
❌ LiteLLM package required but not found
```
**Solution**: Install LiteLLM: `pip install litellm`

### Debug Mode
For more detailed output, check the individual test scripts which include debug logging.

## 💡 Testing Strategy

### Development Testing
Run tests frequently during development:
```bash
# Quick smoke test (universal driver only)
python test_universal_driver.py

# Full validation
python run_all_tests.py
```

### CI/CD Testing
For automated testing environments:
```bash
# Skip tests requiring special setup
python run_all_tests.py --skip ollama

# Test only core functionality
python run_all_tests.py --tests openai,universal
```

### Production Validation
Before deploying:
```bash
# Full test suite with real API keys
python run_all_tests.py
```

## 🎯 Next Steps

After successful testing:

1. **Install middleware** for providers you plan to use
2. **Set up environment variables** for your production environment
3. **Use `ReveniumDriver(model="your-model")`** in your applications
4. **Monitor usage** in your Revenium dashboard

The testing suite validates that the universal driver system is ready for production use with any LLM provider! 🚀 