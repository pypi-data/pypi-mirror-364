# MCP Logger Utils - Enhanced Documentation

A comprehensive logging and utility package for MCP (Model Context Protocol) servers with production-ready features.

## Features

### Core Features
- 🔍 **Smart Logging** - Automatic truncation of large data structures
- 🛡️ **PII Protection** - Automatic detection and redaction of sensitive data
- 🔄 **Circular Reference Protection** - Safe logging of complex objects
- 📊 **Performance Monitoring** - Track slow operations automatically
- 🚦 **Rate Limiting** - Prevent log spam
- 🧪 **Testing Utilities** - Capture logs in tests
- 🔧 **Debug Tools** - Process management for MCP servers
- 🎯 **Error Deduplication** - Avoid repeated error messages
- 📝 **Structured Logging** - Add request IDs and context
- ⚙️ **Runtime Configuration** - Change settings without restart

## Installation

```bash
pip install mcp-logger-utils
```

## Quick Start

### Basic Usage

```python
from mcp_logger_utils import MCPLogger

# Create logger instance
logger = MCPLogger("my-mcp-server")

# Use it like any logger
logger.info("Server starting up...")
logger.debug("Debug information")
logger.success("Operation completed successfully ✅")
logger.error("Something went wrong")
```

### Available Logging Methods

All standard loguru methods are available with type hints:

```python
logger.trace("Most detailed logging")
logger.debug("Debug information")
logger.info("General information")
logger.success("Success messages ✅")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical issues")
logger.exception("Log with traceback")
```

## Enhanced Features

### 1. PII Protection

Automatically redact sensitive information:

```python
# Enable PII redaction (enabled by default)
logger = MCPLogger("my-server", enable_pii_redaction=True)

# These will be automatically redacted
logger.info("User email: john.doe@example.com")
# Logs: "User email: j***@***.***"

logger.info("Phone: +1-555-123-4567")
# Logs: "Phone: ***-***-****"

logger.info("SSN: 123-45-6789")
# Logs: "SSN: ***-**-****"

# Toggle at runtime
logger.set_pii_redaction(False)  # Disable
logger.set_pii_redaction(True)   # Re-enable
```

### 2. Performance Monitoring

Track slow operations automatically:

```python
# Set threshold for specific functions
@logger.monitor_performance(threshold_ms=100)
async def process_data():
    await asyncio.sleep(0.2)  # Will log warning

# Or set global thresholds
logger.set_performance_threshold("process_data", 100)

@logger.monitor_performance()
async def process_data():
    # Will use the configured threshold
    pass
```

### 3. Rate Limiting

Prevent log spam:

```python
from datetime import timedelta

# Global rate limiting
logger = MCPLogger(
    "my-server",
    rate_limit_window=timedelta(seconds=60),
    rate_limit_max_calls=100
)

# Per-function rate limiting
@logger.rate_limit(max_calls=5, time_window=timedelta(minutes=1))
def noisy_function():
    logger.info("This won't spam logs")
```

### 4. Testing Utilities

Capture logs in tests:

```python
def test_my_function():
    logger = MCPLogger("test")
    
    with logger.capture() as logs:
        my_function()
        
    # Check captured logs
    assert "Expected message" in logs
    assert len(logs.get_messages("ERROR")) == 0
```

### 5. Structured Logging

Add context to all logs:

```python
# Create logger with request ID
request_logger = logger.with_request_id("req-123")
request_logger.info("Processing request")
# Logs include request_id in extra fields

# Temporary context
with logger.contextualize(user_id=456, session="abc"):
    logger.info("User action")
    # These logs have user_id and session in context
```

### 6. Error Deduplication

Avoid repeated error messages:

```python
# Errors are automatically deduplicated
for i in range(100):
    try:
        risky_operation()
    except Exception as e:
        logger.log_error("risky_operation", 0.1, e, {"attempt": i})
        # Only first error and every 10th duplicate are logged
```

### 7. Debug Tool Decorator

Comprehensive debugging for MCP tools:

```python
from mcp_logger_utils import debug_tool

@debug_tool(logger)
async def fetch_data(url: str):
    # Automatically logs:
    # - Function calls with arguments
    # - Execution time
    # - Return values
    # - Exceptions with full context
    response = await http_client.get(url)
    return response.json()

# With exception catching
@debug_tool(logger, catch_exceptions=True)
async def risky_operation():
    # Returns JSON error instead of raising
    raise ValueError("Something went wrong")
```

### 8. Runtime Configuration

Change settings without restart:

```python
# Change log level
logger.set_level("DEBUG")  # More verbose
logger.set_level("WARNING")  # Less verbose

# Toggle features
logger.set_pii_redaction(False)
logger.enable_pii_redaction = True
```

## MCP Server Integration

### Complete Example

```python
from mcp_logger_utils import MCPLogger, debug_tool, create_debug_tools
from fastmcp import FastMCP

# Initialize
mcp = FastMCP("my-mcp-server")
logger = MCPLogger(
    "my-mcp-server",
    enable_pii_redaction=True,
    rate_limit_window=timedelta(minutes=1),
    rate_limit_max_calls=1000
)

# Add debug tools (for development)
create_debug_tools(mcp, "my-mcp-server", logger)

@mcp.tool()
@debug_tool(logger)
async def process_document(content: str, user_email: str):
    """Process document with automatic logging."""
    logger.info(f"Processing document for {user_email}")
    # Email will be redacted in logs
    
    # Long content will be truncated
    logger.debug(f"Content: {content}")
    
    # Process...
    result = await process(content)
    
    return create_success_response(result)

# Performance monitoring
@mcp.tool()
@logger.monitor_performance(threshold_ms=500)
async def analyze_data(data: list):
    """Analyze data with performance tracking."""
    # Will warn if takes > 500ms
    return await heavy_computation(data)
```

## Circular Reference Protection

```python
# Safe to log circular references
obj1 = {"name": "A", "ref": None}
obj2 = {"name": "B", "ref": obj1}
obj1["ref"] = obj2

logger.info(f"Objects: {obj1}")
# Logs: Objects: {"name": "A", "ref": {"name": "B", "ref": "<circular reference>"}}
```

## Response Utilities

Standardized MCP responses:

```python
from mcp_logger_utils import create_success_response, create_error_response

# Success response
return create_success_response(
    {"data": result},
    tool_name="my_tool",
    start_time=start_time
)

# Error response
return create_error_response(
    "Something went wrong",
    tool_name="my_tool",
    start_time=start_time
)
```

## Debug Tools

For MCP server development:

```python
from mcp_logger_utils import create_debug_tools

# Add debug tools to your MCP server
create_debug_tools(mcp, "my-server", logger)

# This adds:
# - debug_reload_server: Kill old instances and reload
# - debug_list_instances: List running instances
# - debug_clear_cache: Clear UV cache
```

## Environment Variables

- `MCP_LOG_LEVEL`: Set default log level (DEBUG, INFO, WARNING, ERROR)
- `MCP_DEBUG`: Set to "true" or "1" for debug mode
- `MCP_LOG_DIR`: Custom log directory (default: ~/.claude/mcp_logs)

## Best Practices

1. **Initialize early**: Create logger at module level
2. **Use structured logging**: Add context with `contextualize()`
3. **Monitor performance**: Add thresholds for critical operations
4. **Enable PII protection**: Always in production
5. **Set rate limits**: Prevent runaway logging
6. **Use debug_tool**: For all MCP tool functions
7. **Capture in tests**: Verify logging behavior

## Migration from Basic Logger

The enhanced logger is 100% backward compatible. Just update your import:

```python
# Old
from mcp_logger_utils import MCPLogger

# New - no code changes needed!
from mcp_logger_utils import MCPLogger
```

Then add enhanced features as needed.

## License

MIT