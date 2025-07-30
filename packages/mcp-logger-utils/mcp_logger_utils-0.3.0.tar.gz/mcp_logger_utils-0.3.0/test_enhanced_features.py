#!/usr/bin/env python3
"""Test script for enhanced logger features."""

import asyncio
import time
from datetime import timedelta

from src.mcp_logger_utils.enhanced_logger import MCPLogger, debug_tool


async def test_all_features():
    """Test all enhanced features."""
    
    # Create logger with all features enabled
    logger = MCPLogger(
        "test_enhanced",
        log_level="DEBUG",
        enable_pii_redaction=True,
        rate_limit_window=timedelta(seconds=5),
        rate_limit_max_calls=3
    )
    
    print("\n🧪 Testing Enhanced MCPLogger Features\n")
    
    # 1. Test explicit methods with type hints
    print("1️⃣ Testing explicit logging methods:")
    logger.trace("This is a trace message")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message ✅")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # 2. Test circular reference protection
    print("\n2️⃣ Testing circular reference protection:")
    obj1 = {'name': 'obj1', 'ref': None}
    obj2 = {'name': 'obj2', 'ref': obj1}
    obj1['ref'] = obj2  # Create circular reference
    logger.info(f"Circular ref test: {logger._truncate_for_log(obj1)}")
    
    # 3. Test PII redaction
    print("\n3️⃣ Testing PII redaction:")
    logger.info("User email: john.doe@example.com")
    logger.info("Phone: +1-555-123-4567")
    logger.info("SSN: 123-45-6789")
    logger.info("Credit card: 1234-5678-9012-3456")
    logger.info("IP address: 192.168.1.1")
    logger.info("JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    
    # 4. Test log capture for testing
    print("\n4️⃣ Testing log capture:")
    with logger.capture() as logs:
        logger.info("Captured message 1")
        logger.warning("Captured warning")
        logger.error("Captured error")
    
    print(f"  Captured {len(logs.messages)} messages")
    print(f"  Contains 'Captured message 1': {'Captured message 1' in logs}")
    print(f"  Error messages: {logs.get_messages('ERROR')}")
    
    # 5. Test performance monitoring
    print("\n5️⃣ Testing performance monitoring:")
    
    @logger.monitor_performance(threshold_ms=50)
    async def slow_function():
        await asyncio.sleep(0.1)  # 100ms - should trigger warning
        return "done"
    
    @logger.monitor_performance(threshold_ms=200)
    async def fast_function():
        await asyncio.sleep(0.01)  # 10ms - should not trigger warning
        return "done"
    
    await slow_function()
    await fast_function()
    
    # 6. Test rate limiting
    print("\n6️⃣ Testing rate limiting:")
    
    @logger.rate_limit(max_calls=3, time_window=timedelta(seconds=5))
    def rate_limited_function(i):
        logger.info(f"Rate limited call {i}")
        return f"call {i}"
    
    # These should work (first 3 calls)
    for i in range(5):
        result = rate_limited_function(i)
        if result is None:
            print(f"  Call {i} was rate limited")
    
    # 7. Test context management
    print("\n7️⃣ Testing context management:")
    
    # Request ID binding
    request_logger = logger.with_request_id("req-123")
    request_logger.info("This message has request ID")
    
    # Temporary context
    with logger.contextualize(user_id=456, session="abc"):
        logger.info("This message has temporary context")
    
    logger.info("This message has no extra context")
    
    # 8. Test error deduplication
    print("\n8️⃣ Testing error deduplication:")
    
    @debug_tool(logger, catch_exceptions=True)
    def failing_function():
        raise ValueError("This always fails")
    
    # Call multiple times - should deduplicate
    for i in range(5):
        result = failing_function()
        if i == 0:
            print(f"  First error: {result[:50]}...")
    
    # 9. Test runtime configuration
    print("\n9️⃣ Testing runtime configuration:")
    
    # Change log level
    logger.set_level("WARNING")
    logger.debug("This debug message should not appear")
    logger.warning("This warning should appear")
    
    # Change back
    logger.set_level("DEBUG")
    logger.debug("This debug message should appear now")
    
    # Toggle PII redaction
    logger.set_pii_redaction(False)
    logger.info("Email without redaction: test@example.com")
    logger.set_pii_redaction(True)
    logger.info("Email with redaction: test@example.com")
    
    # 10. Test performance threshold configuration
    print("\n🔟 Testing performance threshold configuration:")
    
    logger.set_performance_threshold("custom_function", 25)
    
    @logger.monitor_performance()
    async def custom_function():
        await asyncio.sleep(0.05)  # 50ms - should trigger warning with 25ms threshold
    
    await custom_function()
    
    print("\n✅ All enhanced features tested successfully!")


async def test_backward_compatibility():
    """Test that existing code still works."""
    print("\n🔄 Testing backward compatibility:")
    
    # Original usage pattern
    logger = MCPLogger("backward_compat")
    
    # These should all work via __getattr__
    logger.info("Standard info message")
    logger.success("Success via getattr")
    
    # Original debug_tool should work
    @debug_tool(logger)
    async def original_tool(x: int, y: int):
        return x + y
    
    result = await original_tool(5, 3)
    print(f"  Original tool result: {result}")
    
    print("✅ Backward compatibility maintained!")


if __name__ == "__main__":
    asyncio.run(test_all_features())
    asyncio.run(test_backward_compatibility())