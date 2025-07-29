#!/usr/bin/env python3
"""
Debug script to test Griptape Message construction.
"""

import sys
sys.path.insert(0, '../src')

from griptape.common.prompt_stack.messages.message import Message
from griptape.artifacts import TextArtifact

print("🔍 Testing Griptape Message Construction")
print("=" * 50)

# Test 1: Try list with TextArtifact
print("\n📦 Test 1: List with TextArtifact")
try:
    content = "Hello world"
    message = Message(
        content=[TextArtifact(content)],
        role=Message.ASSISTANT_ROLE
    )
    print("✅ Message created successfully")
    print(f"   Message type: {type(message)}")
    print(f"   Content type: {type(message.content)}")
    print(f"   Content length: {len(message.content)}")
    print(f"   First item type: {type(message.content[0])}")
    
    # Try to get the value
    try:
        value = message.value
        print(f"✅ Message value: {value}")
    except Exception as e:
        print(f"❌ Error getting value: {e}")
        
    # Try to convert to artifact
    try:
        artifact = message.to_artifact()
        print(f"✅ to_artifact() works: {type(artifact)}")
        print(f"   Artifact value: {artifact.value}")
    except Exception as e:
        print(f"❌ Error in to_artifact(): {e}")
        
except Exception as e:
    print(f"❌ Failed to create message: {e}")

# Test 2: Try single TextArtifact (not in list)
print("\n📦 Test 2: Single TextArtifact")
try:
    content = "Hello world"
    message = Message(
        content=TextArtifact(content),
        role=Message.ASSISTANT_ROLE
    )
    print("✅ Message created successfully")
    
    # Try to get the value
    try:
        value = message.value
        print(f"✅ Message value: {value}")
    except Exception as e:
        print(f"❌ Error getting value: {e}")
        
except Exception as e:
    print(f"❌ Failed to create message: {e}")

# Test 3: Examine TextArtifact attributes
print("\n📦 Test 3: TextArtifact attributes")
try:
    artifact = TextArtifact("test")
    print(f"✅ TextArtifact created: {type(artifact)}")
    print(f"   Has .artifact attr: {hasattr(artifact, 'artifact')}")
    print(f"   Has .value attr: {hasattr(artifact, 'value')}")
    print(f"   Value: {artifact.value}")
    print(f"   All attributes: {[attr for attr in dir(artifact) if not attr.startswith('_')]}")
except Exception as e:
    print(f"❌ Error examining TextArtifact: {e}")

print("\n🎯 Debug complete!") 