#!/usr/bin/env python3
"""Test backward compatibility with YouTube transcripts MCP server."""

import asyncio
from datetime import datetime

# Test with enhanced logger but using it like the original
from src.mcp_logger_utils.enhanced_logger import MCPLogger, debug_tool
from src.mcp_logger_utils.response_utils import create_success_response, create_error_response


async def test_youtube_patterns():
    """Test patterns from the YouTube transcripts MCP."""
    
    # Initialize logger exactly like YouTube MCP does
    mcp_logger = MCPLogger("youtube-transcripts")
    
    print("🎥 Testing YouTube MCP compatibility patterns\n")
    
    # Test 1: Standard logging patterns
    print("1️⃣ Testing standard logging:")
    mcp_logger.info("YouTube Transcripts MCP starting up...")
    mcp_logger.info(f"Python version: 3.11")
    mcp_logger.info(f"Server name: youtube-transcripts")
    
    # Test 2: Warning patterns
    print("\n2️⃣ Testing warnings:")
    mcp_logger.warning("No YouTube API key found - some features may be limited")
    
    # Test 3: Debug patterns
    print("\n3️⃣ Testing debug patterns:")
    mcp_logger.debug(f"Using device: cuda")
    mcp_logger.debug(f"Using proxy: proxy.example.com:8080")
    
    # Test 4: Error patterns with log_error
    print("\n4️⃣ Testing error logging:")
    try:
        raise ValueError("Rate limit exceeded")
    except Exception as e:
        error_id = mcp_logger.log_error(
            function="download_transcript_with_proxy",
            duration=1.234,
            error=e,
            context={"video_id": "abc123", "use_proxy": True}
        )
        print(f"  Error logged with ID: {error_id}")
    
    # Test 5: debug_tool decorator
    print("\n5️⃣ Testing debug_tool decorator:")
    
    @debug_tool(mcp_logger)
    async def fetch_video_info(video_id: str):
        """Simulate fetching video info."""
        await asyncio.sleep(0.1)
        return {
            "video_id": video_id,
            "title": "Test Video",
            "duration": 300
        }
    
    result = await fetch_video_info("test123")
    print(f"  Result: {result}")
    
    # Test 6: Response utilities
    print("\n6️⃣ Testing response utilities:")
    success_resp = create_success_response(
        "Transcript fetched successfully",
        tool_name="fetch_transcript",
        start_time=datetime.now().timestamp() - 1.5
    )
    print(f"  Success response created: {len(success_resp)} chars")
    
    error_resp = create_error_response(
        "Rate limited",
        tool_name="youtube_search",
        start_time=datetime.now().timestamp() - 0.5
    )
    print(f"  Error response created: {len(error_resp)} chars")
    
    # Test 7: Using __getattr__ for methods not explicitly defined
    print("\n7️⃣ Testing __getattr__ delegation:")
    mcp_logger.success("Successfully fetched existing captions")
    
    # Test 8: Complex error scenarios
    print("\n8️⃣ Testing complex error scenarios:")
    
    @debug_tool(mcp_logger, catch_exceptions=True)
    async def failing_tool():
        raise RuntimeError("Simulated failure")
    
    error_result = await failing_tool()
    print(f"  Caught error result: {error_result[:50]}...")
    
    # Test 9: Cancellation handling
    print("\n9️⃣ Testing cancellation:")
    
    @debug_tool(mcp_logger)
    async def cancellable_task():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            mcp_logger.warning("Task was cancelled")
            raise
    
    task = asyncio.create_task(cancellable_task())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("  Task cancelled successfully")
    
    print("\n✅ All YouTube MCP patterns work correctly!")


async def test_enhanced_features_dont_interfere():
    """Test that enhanced features don't interfere with normal usage."""
    print("\n🔧 Testing that enhanced features don't interfere:\n")
    
    # Create logger with enhanced features
    logger = MCPLogger(
        "test-enhanced",
        enable_pii_redaction=True,  # This shouldn't affect normal usage
        rate_limit_window=None,  # Not enabled by default
    )
    
    # Should work normally
    logger.info("Normal message without PII")
    logger.info("Message with email: test@example.com")  # Should be redacted
    logger.debug("Debug message")
    logger.error("Error message")
    
    # Original patterns should still work
    try:
        raise Exception("Test error")
    except Exception as e:
        error_id = logger.log_error("test_function", 0.123, e, {})
        print(f"  Error ID: {error_id}")
    
    print("\n✅ Enhanced features don't interfere with normal usage!")


if __name__ == "__main__":
    asyncio.run(test_youtube_patterns())
    asyncio.run(test_enhanced_features_dont_interfere())