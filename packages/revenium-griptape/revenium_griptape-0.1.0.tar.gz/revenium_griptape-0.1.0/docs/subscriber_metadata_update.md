# Subscriber Metadata Structure Update Plan

## Overview

The Revenium API has changed how it accepts subscriber-related metadata from a flat structure to a nested structure. This document outlines a simplified approach to update all Griptape drivers, examples, and documentation to use the new format directly.

**Key Insight**: Since this change hasn't been released yet, we can simply update all code to use the new format without backward compatibility concerns, eliminating the need for transformation utilities.

## Current vs. New Structure

### Current (Flat) Structure
```python
{
    "trace_id": "session-123",
    "task_type": "content-analysis",
    "subscriber_email": "demo@company.com",
    "subscriber_id": "user-456",
    "organization_id": "org-789",
    "subscription_id": "sub-123",
    "product_id": "ai-assistant",
    "agent": "content-analyzer-v1"
}
```

### New (Nested) Structure
```python
{
    "trace_id": "session-123",
    "task_type": "content-analysis",
    "subscriber": {
        "id": "user-456",
        "email": "demo@company.com",
        "credential": {
            "name": "api_key_name",
            "value": "api_key_value"
        }
    },
    "organization_id": "org-789",
    "subscription_id": "sub-123",
    "product_id": "ai-assistant",
    "agent": "content-analyzer-v1"
}
```

## Simplified Implementation Approach

### Why This Approach is Better

**No Transformation Overhead**: Since there's no backward compatibility requirement, we can eliminate the complexity of runtime metadata transformation and simply update all code to use the new format directly.

**Benefits**:
- **Faster Implementation**: 4-5 hours vs 10-15 hours
- **Zero Runtime Overhead**: No transformation on every API call
- **Cleaner Code**: Direct format usage, easier to understand
- **Easier Maintenance**: Fewer components to maintain
- **Future-Proof**: Easy to add new nested fields

### Files Requiring Changes

#### 1. Example Files (7 files)
- `examples/embedding_example.py`
- `examples/universal_driver_example.py`
- `examples/litellm_direct_example.py`
- `examples/litellm_proxy_example.py`
- `examples/openai_example.py`
- `examples/anthropic_example.py`
- `examples/universal_example.py`

#### 2. Testing Files (6 files)
- `testing/test_openai_driver.py`
- `testing/test_anthropic_driver.py`
- `testing/test_ollama_driver.py`
- `testing/test_litellm_driver.py`
- `testing/test_universal_driver.py`
- `testing/debug_headers.py`

#### 3. Driver Implementation Files (1 file needs changes)
- `src/revenium_griptape/drivers/revenium_litellm_driver.py` (header handling only)

#### 4. Documentation Files (4 files)
- `README.md`
- `README_Universal_Drivers.md`
- `examples/README.md`
- `testing/README.md`

**Note**: Most driver files (OpenAI, Anthropic, Ollama, Universal) require no changes since they simply pass through metadata to the underlying middleware packages.

## Implementation Plan

### Phase 1: Update Examples and Tests (1-2 hours)

**Objective**: Update all metadata dictionaries to use the new nested subscriber format.

**Approach**: Simple find/replace operations across all example and test files. No logic changes needed since drivers pass through metadata unchanged.

**Files to Update**:
- All 7 example files
- All 6 testing files

**Example Change** (`examples/embedding_example.py` Lines 16-22):

**Before**:
```python
common_metadata = {
    "trace_id": "griptape-demo-123",
    "task_type": "content-analysis",
    "subscriber_email": "demo@company.com",
    "organization_id": "org-456",
    "agent": "content-analyzer-v1"
}
```

**After**:
```python
common_metadata = {
    "trace_id": "griptape-demo-123",
    "task_type": "content-analysis",
    "subscriber": {
        "id": "demo-user-456",
        "email": "demo@company.com",
        "credential": {
            "name": "demo_api_key",
            "value": "demo_key_value"
        }
    },
    "organization_id": "org-456",
    "agent": "content-analyzer-v1"
}
```

**Implementation**: Apply the same pattern to all metadata dictionaries across examples and tests.

### Phase 2: Update LiteLLM Driver Header Handling (1 hour)

**Objective**: Modify the LiteLLM driver to handle nested subscriber objects in HTTP headers.

**File**: `src/revenium_griptape/drivers/revenium_litellm_driver.py`

**Current Code** (Lines 210-214):
```python
# Inject metadata via x-revenium-* headers (official approach)
if self.usage_metadata:
    for key, value in self.usage_metadata.items():
        # Convert key to proper header format
        header_key = f"x-revenium-{key.replace('_', '-')}"
        headers[header_key] = str(value)
```

**Updated Code**:
```python
# Inject metadata via x-revenium-* headers (official approach)
if self.usage_metadata:
    for key, value in self.usage_metadata.items():
        if key == 'subscriber' and isinstance(value, dict):
            # Handle nested subscriber object as JSON
            import json
            header_key = f"x-revenium-{key.replace('_', '-')}"
            headers[header_key] = json.dumps(value)
        else:
            # Convert key to proper header format
            header_key = f"x-revenium-{key.replace('_', '-')}"
            headers[header_key] = str(value)
```

**Rationale**: JSON encoding preserves the nested structure while remaining compatible with HTTP headers.

### Phase 3: Update Documentation (1 hour)

**Objective**: Update all documentation to show only the new nested format.

**Tasks**:
1. Remove all references to old flat field names (`subscriber_email`, `subscriber_id`)
2. Update metadata tables and examples
3. Update quick start guides

**Key Changes**:

**README.md Metadata Table** (Lines 175-183):
```markdown
| Field | Description | Example |
|-------|-------------|---------|
| `trace_id` | Session or conversation ID | `"chat-session-123"` |
| `task_type` | Type of AI task | `"summarization"`, `"qa"` |
| `subscriber` | User information object | `{"id": "user-456", "email": "user@company.com"}` |
| `subscriber.id` | User ID | `"user-456"` |
| `subscriber.email` | User email | `"user@company.com"` |
| `subscriber.credential` | API credential info | `{"name": "api_key", "value": "key_value"}` |
| `organization_id` | Team or department | `"sales-team"` |
| `subscription_id` | Billing plan | `"enterprise-plan"` |
| `product_id` | Product or feature | `"ai-assistant"` |
| `agent` | AI agent identifier | `"support-bot-v2"` |
```

### Phase 4: Validation Testing (1 hour)

**Objective**: Ensure all components work correctly with the new format.

**Tasks**:
1. Run all existing tests to verify they pass
2. Test each example manually to ensure they work
3. Verify LiteLLM header generation with nested objects
4. Test integration with actual middleware packages

## Testing Strategy

### Validation Tests
1. **Format Verification**: Ensure all metadata uses new nested structure
2. **Driver Integration**: Test each driver passes through nested metadata correctly
3. **Header Generation**: Verify LiteLLM driver creates correct headers for nested objects
4. **Middleware Compatibility**: Test with actual middleware packages
5. **API Integration**: Verify Revenium API accepts new format

### Test Execution
1. **Unit Tests**: Run existing test suite with updated metadata
2. **Example Testing**: Execute all examples to ensure they work
3. **Integration Testing**: Test with real API endpoints
4. **Performance Testing**: Verify no performance degradation

## Risk Mitigation

### Potential Issues
1. **Middleware Compatibility**: Ensure all middleware packages support new structure
2. **Header Size Limits**: JSON-encoded subscriber objects in headers
3. **API Compatibility**: Verify Revenium API accepts new format

### Mitigation Strategies
1. **Incremental Testing**: Test one component at a time
2. **Header Validation**: Verify JSON encoding works with HTTP headers
3. **API Validation**: Test with actual Revenium endpoints
4. **Rollback Plan**: Keep original files until validation complete

## Success Criteria

1. **All examples work** with new metadata structure
2. **All tests pass** with updated metadata
3. **Documentation accurately reflects** new structure
4. **No performance degradation** in driver operations
5. **Successful integration** with updated Revenium API
6. **Clean, maintainable code** without transformation overhead

## Timeline Estimate

- **Phase 1**: 1-2 hours (Update examples and tests)
- **Phase 2**: 1 hour (LiteLLM driver header handling)
- **Phase 3**: 1 hour (Documentation updates)
- **Phase 4**: 1 hour (Validation testing)

**Total Estimated Time**: 4-5 hours

## Detailed Code Changes

### Phase 1: Example and Test Updates

**Pattern**: Replace all metadata dictionaries with new nested subscriber format.

**Example Files to Update**:

**`examples/embedding_example.py`** (Lines 16-22):
```python
# OLD
common_metadata = {
    "trace_id": "griptape-demo-123",
    "task_type": "content-analysis",
    "subscriber_email": "demo@company.com",
    "organization_id": "org-456",
    "agent": "content-analyzer-v1"
}

# NEW
common_metadata = {
    "trace_id": "griptape-demo-123",
    "task_type": "content-analysis",
    "subscriber": {
        "id": "demo-user-456",
        "email": "demo@company.com",
        "credential": {
            "name": "demo_api_key",
            "value": "demo_key_value"
        }
    },
    "organization_id": "org-456",
    "agent": "content-analyzer-v1"
}
```

**`examples/universal_driver_example.py`** (Lines 16-22):
```python
# OLD
common_metadata = {
    "trace_id": "universal-demo-456",
    "task_type": "multi-provider-analysis",
    "subscriber_email": "demo@company.com",
    "organization_id": "org-789",
    "agent": "universal-analyzer-v2"
}

# NEW
common_metadata = {
    "trace_id": "universal-demo-456",
    "task_type": "multi-provider-analysis",
    "subscriber": {
        "id": "demo-user-789",
        "email": "demo@company.com",
        "credential": {
            "name": "universal_api_key",
            "value": "universal_key_value"
        }
    },
    "organization_id": "org-789",
    "agent": "universal-analyzer-v2"
}
```

**Test Files**: Apply the same pattern to all test metadata dictionaries.

### Phase 2: LiteLLM Driver Header Handling

**File**: `src/revenium_griptape/drivers/revenium_litellm_driver.py`

**Current Code** (Lines 210-214):
```python
# Inject metadata via x-revenium-* headers (official approach)
if self.usage_metadata:
    for key, value in self.usage_metadata.items():
        # Convert key to proper header format
        header_key = f"x-revenium-{key.replace('_', '-')}"
        headers[header_key] = str(value)
```

**Updated Code**:
```python
# Inject metadata via x-revenium-* headers (official approach)
if self.usage_metadata:
    for key, value in self.usage_metadata.items():
        if key == 'subscriber' and isinstance(value, dict):
            # Handle nested subscriber object as JSON
            import json
            header_key = f"x-revenium-{key.replace('_', '-')}"
            headers[header_key] = json.dumps(value)
            logger.debug(f"Injected nested subscriber as JSON header: {header_key}")
        else:
            # Convert key to proper header format
            header_key = f"x-revenium-{key.replace('_', '-')}"
            headers[header_key] = str(value)
```

**Rationale**: JSON encoding preserves the nested structure while remaining compatible with HTTP headers. The middleware can parse the JSON to reconstruct the nested object.

### Phase 3: Documentation Updates

**README.md Metadata Table** (Lines 175-183):

**Before**:
```markdown
| Field | Description | Example |
|-------|-------------|---------|
| `trace_id` | Session or conversation ID | `"chat-session-123"` |
| `task_type` | Type of AI task | `"summarization"`, `"qa"` |
| `subscriber_email` | User email | `"user@company.com"` |
| `subscriber_id` | User ID | `"user-456"` |
| `organization_id` | Team or department | `"sales-team"` |
```

**After**:
```markdown
| Field | Description | Example |
|-------|-------------|---------|
| `trace_id` | Session or conversation ID | `"chat-session-123"` |
| `task_type` | Type of AI task | `"summarization"`, `"qa"` |
| `subscriber` | User information object | `{"id": "user-456", "email": "user@company.com"}` |
| `subscriber.id` | User ID | `"user-456"` |
| `subscriber.email` | User email | `"user@company.com"` |
| `subscriber.credential` | API credential info | `{"name": "api_key", "value": "key_value"}` |
| `organization_id` | Team or department | `"sales-team"` |
```

**README_Universal_Drivers.md** (Lines 98-103):

**Before**:
```python
usage_metadata={
    "trace_id": "user-session-123",
    "task_type": "content-generation",
    "subscriber_email": "user@example.com",
    "organization_id": "org-456"
}
```

**After**:
```python
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
```

## Implementation Priority

### Recommended Execution Order

1. **Start with one example**: Update `examples/embedding_example.py` and test it end-to-end
2. **Update LiteLLM driver**: Implement JSON header encoding for nested objects
3. **Batch update remaining examples**: Apply the same pattern to all example files
4. **Update all tests**: Apply the same pattern to all test files
5. **Update documentation**: Remove old format references, add new format examples
6. **Final validation**: Run comprehensive tests with all middleware packages

### Key Benefits of This Approach

- **60% faster implementation** (4-5 hours vs 10-15 hours)
- **Zero runtime overhead** (no transformation on every API call)
- **Cleaner, more maintainable code** (direct format usage)
- **Future-proof design** (easy to extend nested structure)
- **Immediate validation** (easy to test each change)

This simplified approach eliminates unnecessary complexity while achieving the exact same goal: updating all Griptape components to use the new nested subscriber metadata structure required by the updated Revenium API.
