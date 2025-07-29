#!/usr/bin/env python3
"""
Debug script to test LiteLLM proxy connection and model names.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, '../src')

print("🔍 Testing LiteLLM Proxy Connection")
print("=" * 50)

# Check environment
proxy_url = os.getenv('LITELLM_PROXY_URL')
proxy_key = os.getenv('LITELLM_API_KEY')

print(f"Proxy URL: {proxy_url}")
print(f"Has API Key: {bool(proxy_key)}")

if not proxy_url or not proxy_key:
    print("❌ Missing proxy configuration")
    sys.exit(1)

try:
    import litellm
    print("✅ LiteLLM imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LiteLLM: {e}")
    sys.exit(1)

# Test 1: Direct LiteLLM call with openai/gpt-4o-mini
print("\n📞 Test 1: Direct LiteLLM call")
try:
    response = litellm.completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: Direct call with openai/gpt-4o-mini")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Direct call - {e}")

# Test 2: Try without openai/ prefix
print("\n📞 Test 2: Without openai/ prefix")
try:
    response = litellm.completion(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: Direct call with gpt-4o-mini")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Without prefix - {e}")

# Test 3: Try with different model from the list
print("\n📞 Test 3: Google Gemini model")
try:
    response = litellm.completion(
        model='google/gemini-pro',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: Direct call with google/gemini-pro")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Google Gemini - {e}")

# Test 4: Try with custom headers (sometimes proxies need this)
print("\n📞 Test 4: With custom headers")
try:
    response = litellm.completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20,
        custom_llm_provider="openai"  # Force OpenAI provider
    )
    print("✅ SUCCESS: With custom provider")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Custom provider - {e}")

# Test 5: Try using the exact model ID from your list
print("\n📞 Test 5: Using base_url instead of api_base")
try:
    response = litellm.completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        base_url=proxy_url,  # Use base_url instead of api_base
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: Using base_url")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: base_url - {e}")

# Test 6: Try with litellm.set_verbose = True for more debugging
print("\n📞 Test 6: With verbose debugging")
try:
    litellm.set_verbose = True
    response = litellm.completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: With verbose debugging")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Verbose debug - {e}")
finally:
    litellm.set_verbose = False

# Test 7: Use custom provider to bypass automatic transformation
print("\n📞 Test 7: Custom provider bypass")
try:
    response = litellm.completion(
        model='openai/gpt-4o-mini',
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20,
        custom_llm_provider="custom"  # Use "custom" to bypass processing
    )
    print("✅ SUCCESS: Custom provider bypass")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Custom provider bypass - {e}")

# Test 8: Use a different approach - set model as a custom provider format
print("\n📞 Test 8: Custom format")
try:
    response = litellm.completion(
        model='custom/openai/gpt-4o-mini',  # Prefix with custom/
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        api_base=proxy_url,
        api_key=proxy_key,
        max_tokens=20
    )
    print("✅ SUCCESS: Custom format")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Custom format - {e}")

# Test 9: Try using litellm's proxy client specifically  
print("\n📞 Test 9: LiteLLM Proxy Client")
try:
    # Use the proxy-specific approach
    import openai
    client = openai.OpenAI(
        api_key=proxy_key,
        base_url=proxy_url
    )
    response = client.chat.completions.create(
        model='openai/gpt-4o-mini',  # Send exact model name
        messages=[{'role': 'user', 'content': 'Say "test successful"'}],
        max_tokens=20
    )
    print("✅ SUCCESS: Direct OpenAI client")
    print(f"   Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ FAILED: Direct OpenAI client - {e}")

print("\n🎯 Debug complete!") 