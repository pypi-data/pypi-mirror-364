#!/usr/bin/env python3
"""Test script that simulates importing from debug project context."""

import subprocess
import sys

# Test command that would be run in debug project
test_command = '''
from mcp_logger_utils import MCPLogger
logger = MCPLogger("debug_test")
logger.info("Testing from debug project context")
print("SUCCESS: mcp_logger_utils works in debug project!")
'''

# Run the test
result = subprocess.run(
    [sys.executable, "-c", test_command],
    cwd="/home/graham/workspace/experiments/debug",
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")