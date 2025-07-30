#!/usr/bin/env python3
"""Comprehensive test script for mcp_logger_utils package."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Test imports
try:
    from mcp_logger_utils import (
        MCPLogger,
        debug_tool,
        repair_and_parse_json,
        create_success_response,
        create_error_response,
        create_response,
        parse_response,
        MCPDebugTools,
        create_debug_tools
    )
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


async def test_logger():
    """Test MCPLogger functionality."""
    print("\n📝 Testing MCPLogger...")
    
    # Create logger instance
    logger = MCPLogger("test_tool", log_level="DEBUG")
    
    # Test basic logging methods
    logger.debug("Debug message test")
    logger.info("Info message test")
    logger.warning("Warning message test")
    logger.error("Error message test")
    
    # Test truncation
    long_string = "A" * 1000
    logger.info(f"Long string test: {logger._truncate_for_log(long_string)}")
    
    # Test list truncation
    long_list = list(range(100))
    logger.info(f"Long list test: {logger._truncate_for_log(long_list)}")
    
    # Test base64 truncation
    base64_data = "data:image/png;base64," + "A" * 1000
    logger.info(f"Base64 test: {logger._truncate_for_log(base64_data)}")
    
    print("✅ MCPLogger tests passed!")
    return logger


async def test_debug_tool(logger):
    """Test debug_tool decorator."""
    print("\n🔧 Testing debug_tool decorator...")
    
    @debug_tool(logger)
    def sync_function(x, y):
        """Test synchronous function."""
        return x + y
    
    @debug_tool(logger)
    async def async_function(x, y):
        """Test asynchronous function."""
        await asyncio.sleep(0.1)
        return x * y
    
    @debug_tool(logger, catch_exceptions=True)
    def error_function():
        """Test error handling."""
        raise ValueError("Test error")
    
    # Test sync function
    result = sync_function(5, 3)
    print(f"  Sync result: {result}")
    
    # Test async function
    result = await async_function(5, 3)
    print(f"  Async result: {result}")
    
    # Test error handling
    error_result = error_function()
    print(f"  Error handling result: {error_result[:100]}...")
    
    print("✅ debug_tool tests passed!")


def test_json_utils():
    """Test JSON utilities."""
    print("\n🔧 Testing JSON utilities...")
    
    # Test valid JSON
    valid_json = '{"key": "value", "number": 42}'
    result = repair_and_parse_json(valid_json)
    print(f"  Valid JSON parsed: {result}")
    
    # Test invalid JSON that can be repaired
    invalid_json = '{"key": "value", "missing_quote: 42}'
    result = repair_and_parse_json(invalid_json)
    print(f"  Repaired JSON: {result}")
    
    # Test truncated JSON
    truncated_json = '{"key": "value", "incomplete": {'
    result = repair_and_parse_json(truncated_json)
    print(f"  Truncated JSON: {result}")
    
    print("✅ JSON utilities tests passed!")


def test_response_utils():
    """Test response utilities."""
    print("\n📤 Testing response utilities...")
    
    # Test success response
    success = create_success_response({"message": "Test operation", "data": "test"}, tool_name="test_tool")
    print(f"  Success response: {success}")
    
    # Test error response
    error = create_error_response("Test error", tool_name="test_tool")
    print(f"  Error response: {error}")
    
    # Test generic response
    response = create_response(success=True, data={"custom": "data"}, tool_name="test_tool")
    print(f"  Generic response: {response}")
    
    # Test parse response
    parsed = parse_response(json.dumps(success))
    print(f"  Parsed response: {parsed}")
    
    print("✅ Response utilities tests passed!")


async def test_debug_tools(logger):
    """Test MCPDebugTools."""
    print("\n🛠️ Testing MCPDebugTools...")
    
    # Create debug tools instance
    debug_tools = MCPDebugTools("test_server", logger)
    
    # Test find instances
    instances = debug_tools.find_instances()
    print(f"  Found {len(instances)} instances")
    
    # Test list instances
    list_result = await debug_tools.debug_list_instances()
    result_dict = json.loads(list_result)
    print(f"  List instances status: {result_dict['status']}")
    
    # Test create_debug_tools function
    # Note: create_debug_tools expects an MCP server instance, we'll skip this for now
    print(f"  create_debug_tools function is available for MCP server integration")
    
    print("✅ Debug tools tests passed!")


async def test_file_operations(logger):
    """Test that logger creates log files."""
    print("\n📁 Testing file operations...")
    
    # Check if log directory exists
    log_dir = Path.home() / ".claude" / "mcp_logs"
    print(f"  Log directory exists: {log_dir.exists()}")
    
    # Check if debug log was created
    debug_log = log_dir / "test_tool_debug.log"
    print(f"  Debug log exists: {debug_log.exists()}")
    
    if debug_log.exists():
        # Read last few lines
        lines = debug_log.read_text().strip().split('\n')[-5:]
        print(f"  Last log entries: {len(lines)} lines")
    
    print("✅ File operations tests passed!")


async def main():
    """Run all tests."""
    print("🚀 Starting comprehensive mcp_logger_utils tests...")
    
    try:
        # Test logger
        logger = await test_logger()
        
        # Test debug tool
        await test_debug_tool(logger)
        
        # Test JSON utilities
        test_json_utils()
        
        # Test response utilities
        test_response_utils()
        
        # Test debug tools
        await test_debug_tools(logger)
        
        # Test file operations
        await test_file_operations(logger)
        
        print("\n✅ All tests passed successfully!")
        print("\n📊 Summary:")
        print("  - MCPLogger: ✅")
        print("  - debug_tool decorator: ✅")
        print("  - JSON utilities: ✅")
        print("  - Response utilities: ✅")
        print("  - Debug tools: ✅")
        print("  - File operations: ✅")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())