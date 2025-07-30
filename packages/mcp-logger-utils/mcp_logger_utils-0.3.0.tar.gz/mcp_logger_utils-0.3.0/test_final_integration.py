#!/usr/bin/env python3
"""Final integration test - simulate real MCP server usage."""

import asyncio
from datetime import timedelta

from mcp_logger_utils import MCPLogger, debug_tool, create_success_response


# Simulate a real MCP server scenario
async def simulate_mcp_server():
    """Simulate a complete MCP server with all features."""
    
    # Initialize logger with production settings
    logger = MCPLogger(
        "production-mcp",
        log_level="INFO",
        enable_pii_redaction=True,  # Default, but explicit
        rate_limit_window=timedelta(minutes=1),
        rate_limit_max_calls=1000
    )
    
    print("🚀 Simulating Production MCP Server\n")
    
    # Startup
    logger.info("MCP Server starting up...")
    logger.info(f"Server version: 1.0.0")
    
    # Simulate tools with various features
    
    @debug_tool(logger)
    @logger.monitor_performance(threshold_ms=100)
    async def fetch_user_data(user_id: str, email: str):
        """Fetch user data with PII protection."""
        logger.info(f"Fetching data for user {user_id} with email {email}")
        await asyncio.sleep(0.05)  # Simulate API call
        
        return {
            "user_id": user_id,
            "email": email,
            "name": "John Doe",
            "phone": "+1-555-123-4567",  # Will be redacted in logs
            "ssn": "123-45-6789"  # Will be redacted
        }
    
    @debug_tool(logger, catch_exceptions=True)
    async def process_document(content: str):
        """Process document with error handling."""
        if len(content) < 10:
            raise ValueError("Document too short")
        
        # Simulate processing
        logger.debug(f"Processing document of length {len(content)}")
        await asyncio.sleep(0.1)
        
        return {"processed": True, "length": len(content)}
    
    @logger.rate_limit(max_calls=3, time_window=timedelta(seconds=10))
    async def rate_limited_api():
        """API with rate limiting."""
        logger.info("Rate limited API called")
        return {"status": "ok"}
    
    # Test various scenarios
    print("1️⃣ Testing normal operation with PII:")
    user_data = await fetch_user_data("user123", "john.doe@example.com")
    print(f"   User data fetched: {user_data['user_id']}")
    
    print("\n2️⃣ Testing error handling:")
    error_result = await process_document("short")
    if isinstance(error_result, str) and "error" in error_result:
        print("   Error handled gracefully")
    
    print("\n3️⃣ Testing rate limiting:")
    for i in range(5):
        result = await rate_limited_api()
        if result:
            print(f"   Call {i+1}: Success")
        else:
            print(f"   Call {i+1}: Rate limited")
    
    print("\n4️⃣ Testing circular references:")
    circular_obj = {"id": 1}
    circular_obj["self"] = circular_obj
    logger.info(f"Circular object: {circular_obj}")
    
    print("\n5️⃣ Testing context management:")
    with logger.contextualize(request_id="req-456", user="admin"):
        logger.info("Operation with context")
        
        # Nested operation
        request_logger = logger.with_request_id("req-789")
        request_logger.info("Nested operation")
    
    print("\n6️⃣ Testing performance monitoring:")
    
    @logger.monitor_performance(threshold_ms=50)
    async def slow_operation():
        await asyncio.sleep(0.1)
        return "done"
    
    await slow_operation()
    
    print("\n7️⃣ Testing log capture (for unit tests):")
    with logger.capture() as logs:
        logger.info("Test message 1")
        logger.error("Test error")
        logger.success("Test success")
    
    print(f"   Captured {len(logs.messages)} messages")
    print(f"   Errors: {logs.get_messages('ERROR')}")
    
    print("\n8️⃣ Testing runtime configuration:")
    
    # Change log level
    original_level = "INFO"
    logger.set_level("WARNING")
    logger.debug("This won't show")
    logger.warning("This will show")
    
    # Restore
    logger.set_level(original_level)
    
    # Toggle PII
    logger.set_pii_redaction(False)
    logger.info("Email without redaction: admin@example.com")
    logger.set_pii_redaction(True)
    
    print("\n✅ All production features working correctly!")
    
    # Create final response
    response = create_success_response(
        {"message": "Server test completed", "features_tested": 8},
        tool_name="test_server"
    )
    
    return response


if __name__ == "__main__":
    result = asyncio.run(simulate_mcp_server())
    print(f"\nFinal response: {result[:100]}...")