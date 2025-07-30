"""Enhanced MCP Logger with production-ready features."""

import asyncio
import contextlib
import hashlib
import json
import os
import re
import sys
import time
import traceback
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from inspect import iscoroutinefunction
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, TypeVar, Tuple
from contextvars import ContextVar

from loguru import logger as loguru_logger

# Type variable for decorators
T = TypeVar('T', bound=Callable[..., Any])

# Context variables for structured logging
_request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
_user_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar('user_context', default=None)

# Regex patterns
BASE64_IMAGE_PATTERN = re.compile(r"^(data:image/[a-zA-Z+.-]+;base64,)")

# PII patterns - common patterns to detect and redact
PII_PATTERNS = {
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b'),
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    'jwt': re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),
}


class LogCapture:
    """Context manager for capturing log messages during tests."""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.handler_id = None
        
    def __enter__(self):
        """Start capturing logs."""
        def sink(message):
            record = message.record
            self.messages.append({
                'level': record['level'].name,
                'message': record['message'],
                'time': record['time'],
                'extra': record.get('extra', {}),
                'exception': record.get('exception'),
            })
        
        self.handler_id = loguru_logger.add(sink, level="TRACE")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing logs."""
        if self.handler_id is not None:
            loguru_logger.remove(self.handler_id)
    
    def __contains__(self, text: str) -> bool:
        """Check if text appears in any captured message."""
        return any(text in msg['message'] for msg in self.messages)
    
    def get_messages(self, level: Optional[str] = None) -> List[str]:
        """Get all messages, optionally filtered by level."""
        if level:
            return [msg['message'] for msg in self.messages if msg['level'] == level.upper()]
        return [msg['message'] for msg in self.messages]


class RateLimiter:
    """Rate limiter for preventing log spam."""
    
    def __init__(self, max_calls: int, time_window: timedelta):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, deque] = defaultdict(deque)
    
    def should_allow(self, key: str) -> bool:
        """Check if a call should be allowed."""
        now = datetime.now()
        calls = self.calls[key]
        
        # Remove old calls outside the time window
        while calls and calls[0] < now - self.time_window:
            calls.popleft()
        
        # Check if we're under the limit
        if len(calls) < self.max_calls:
            calls.append(now)
            return True
        
        return False


class MCPLogger:
    """
    Enhanced MCP Logger with production-ready features.
    
    Features:
    - Circular reference protection
    - Explicit methods with type hints
    - Testing utilities
    - Performance monitoring
    - PII detection and redaction
    - Rate limiting
    - Structured logging with context
    - Runtime configuration
    """
    
    def __init__(
        self,
        tool_name: str,
        log_level: Optional[str] = None,
        max_log_str_len: int = 256,
        max_log_list_len: int = 10,
        enable_pii_redaction: bool = True,
        rate_limit_window: Optional[timedelta] = None,
        rate_limit_max_calls: Optional[int] = None,
    ):
        """
        Initialize the Enhanced MCP Logger.
        
        Args:
            tool_name: Name of the tool/server
            log_level: Console logging level
            max_log_str_len: Max string length before truncation
            max_log_list_len: Max list elements before summarizing
            enable_pii_redaction: Whether to auto-redact PII
            rate_limit_window: Time window for rate limiting
            rate_limit_max_calls: Max calls within the window
        """
        self.tool_name = tool_name
        self._logger = loguru_logger.bind(tool_name=tool_name)
        
        # Configuration
        self.max_log_str_len = max_log_str_len
        self.max_log_list_len = max_log_list_len
        self.enable_pii_redaction = enable_pii_redaction
        
        # Rate limiting
        if rate_limit_window and rate_limit_max_calls:
            self.rate_limiter = RateLimiter(rate_limit_max_calls, rate_limit_window)
        else:
            self.rate_limiter = None
        
        # Error deduplication
        self.error_hashes: Set[str] = set()
        self.duplicate_counts: Dict[str, int] = defaultdict(int)
        
        # Performance tracking
        self.performance_thresholds: Dict[str, float] = {}
        
        # Setup logging
        log_dir_str = os.getenv("MCP_LOG_DIR", str(Path.home() / ".claude" / "mcp_logs"))
        self.log_dir = Path(log_dir_str)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine log level
        level = log_level or os.getenv("MCP_LOG_LEVEL", "INFO")
        if os.getenv("MCP_DEBUG", "false").lower() in ("true", "1"):
            level = "DEBUG"
        
        # Configure logger
        self._logger.remove()
        self._logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[tool_name]}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
            )
        )
        
        self.debug_log = self.log_dir / f"{self.tool_name}_debug.log"
        self._logger.add(
            self.debug_log,
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[tool_name]}:{name}:{function}:{line} - {message}"
        )
        
        self.log_startup_info()
    
    def log_startup_info(self):
        """Log startup information."""
        self._logger.info(f"Logger initialized for '{self.tool_name}'. PID: {os.getpid()}")
        self._logger.debug(f"Log directory: {self.log_dir}")
        if self.enable_pii_redaction:
            self._logger.debug("PII redaction enabled")
        if self.rate_limiter:
            self._logger.debug("Rate limiting enabled")
    
    def _truncate_for_log(self, value: Any, _seen: Optional[Set[int]] = None) -> Any:
        """
        Recursively truncate large values with circular reference protection.
        
        Args:
            value: The value to truncate
            _seen: Set of object IDs we've already processed (internal use)
        """
        if _seen is None:
            _seen = set()
        
        # Check for circular references (only for mutable objects)
        if isinstance(value, (dict, list)) and id(value) in _seen:
            return "<circular reference>"
        
        if isinstance(value, str):
            # Redact PII if enabled
            if self.enable_pii_redaction:
                value = self._redact_pii(value)
            
            # Handle base64 images
            match = BASE64_IMAGE_PATTERN.match(value)
            if match:
                header = match.group(1)
                data = value[len(header):]
                if len(data) > self.max_log_str_len:
                    half_len = self.max_log_str_len // 2
                    truncated_data = f"{data[:half_len]}...[truncated]...{data[-half_len:]}"
                    return header + truncated_data
                return value
            elif len(value) > self.max_log_str_len:
                half_len = self.max_log_str_len // 2
                return f"{value[:half_len]}...[truncated]...{value[-half_len:]}"
            return value
        
        elif isinstance(value, list):
            _seen.add(id(value))
            if len(value) > self.max_log_list_len:
                element_type = type(value[0]).__name__ if value else "element"
                return f"[<{len(value)} {element_type}s>]"
            result = [self._truncate_for_log(item, _seen) for item in value]
            _seen.discard(id(value))
            return result
        
        elif isinstance(value, dict):
            _seen.add(id(value))
            result = {k: self._truncate_for_log(v, _seen) for k, v in value.items()}
            _seen.discard(id(value))
            return result
        
        return value
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text."""
        if not isinstance(text, str):
            return text
        
        for pii_type, pattern in PII_PATTERNS.items():
            if pii_type == 'email':
                text = pattern.sub(lambda m: f"{m.group(0)[0]}***@***.***", text)
            elif pii_type == 'phone':
                text = pattern.sub("***-***-****", text)
            elif pii_type == 'ssn':
                text = pattern.sub("***-**-****", text)
            elif pii_type == 'credit_card':
                text = pattern.sub("****-****-****-****", text)
            elif pii_type == 'ip_address':
                text = pattern.sub("***.***.***.***", text)
            elif pii_type == 'jwt':
                text = pattern.sub("***JWT_TOKEN***", text)
        
        return text
    
    def _safe_json_dumps(self, data: Any, **kwargs) -> str:
        """Safely dump data to JSON with truncation and PII redaction."""
        truncated_data = self._truncate_for_log(data)
        
        def default_serializer(o: Any) -> Any:
            if isinstance(o, (datetime, Path)):
                return str(o)
            if hasattr(o, '__dict__'):
                return self._truncate_for_log(o.__dict__)
            try:
                return f"<<non-serializable: {type(o).__name__}>>"
            except Exception:
                return "<<non-serializable>>"
        
        return json.dumps(truncated_data, default=default_serializer, **kwargs)
    
    def _should_log(self, key: Optional[str] = None) -> bool:
        """Check if we should log based on rate limiting."""
        if not self.rate_limiter or not key:
            return True
        return self.rate_limiter.should_allow(key)
    
    def _get_error_hash(self, error: Exception) -> str:
        """Generate a hash for error deduplication."""
        error_str = f"{type(error).__name__}:{str(error)}"
        return hashlib.md5(error_str.encode()).hexdigest()[:8]
    
    # Explicit logging methods with type hints
    def trace(self, message: str, *args, **kwargs) -> None:
        """Log a trace message (most detailed level)."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.trace(message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log a debug message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log an info message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.info(message, *args, **kwargs)
    
    def success(self, message: str, *args, **kwargs) -> None:
        """Log a success message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.success(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log a warning message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log an error message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log a critical message."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Log an exception with traceback."""
        if self._should_log(kwargs.get('rate_limit_key')):
            if self.enable_pii_redaction:
                message = self._redact_pii(message)
            self._logger.exception(message, *args, **kwargs)
    
    # Enhanced methods
    def log_call(self, function: str, duration: float, result: Optional[Any] = None):
        """Log a successful tool call."""
        self._logger.info(f"✓ {function} completed in {duration:.3f}s")
        self._logger.debug(f"Result: {self._safe_json_dumps(result)}")
    
    def log_error(self, function: str, duration: float, error: Exception, context: Dict[str, Any]) -> str:
        """Log an error with deduplication."""
        error_hash = self._get_error_hash(error)
        
        # Check for duplicates
        if error_hash in self.error_hashes:
            self.duplicate_counts[error_hash] += 1
            if self.duplicate_counts[error_hash] % 10 == 0:  # Log every 10th duplicate
                self._logger.warning(
                    f"Error '{error_hash}' has occurred {self.duplicate_counts[error_hash]} times"
                )
            return error_hash
        
        self.error_hashes.add(error_hash)
        error_id = str(uuid.uuid4())
        
        self._logger.error(f"✗ {function} failed in {duration:.3f}s. Error ID: {error_id} (Hash: {error_hash})")
        self._logger.error(f"{type(error).__name__}: {error}")
        self._logger.debug(f"Error Context: {self._safe_json_dumps(context, indent=2)}")
        self._logger.debug(f"Traceback:\n{traceback.format_exc()}")
        
        return error_id
    
    # Context management
    def with_request_id(self, request_id: str) -> 'MCPLogger':
        """Create a logger bound with a request ID."""
        bound_logger = MCPLogger(
            self.tool_name,
            max_log_str_len=self.max_log_str_len,
            max_log_list_len=self.max_log_list_len,
            enable_pii_redaction=self.enable_pii_redaction,
        )
        bound_logger._logger = self._logger.bind(request_id=request_id)
        return bound_logger
    
    @contextlib.contextmanager
    def contextualize(self, **kwargs):
        """Temporarily add context to all logs within this block."""
        contextualized = self._logger.contextualize(**kwargs)
        token = contextualized.__enter__()
        try:
            yield self
        finally:
            contextualized.__exit__(None, None, None)
    
    # Performance monitoring
    def set_performance_threshold(self, function_name: str, threshold_ms: float):
        """Set a performance threshold for a function."""
        self.performance_thresholds[function_name] = threshold_ms / 1000.0
    
    def monitor_performance(self, threshold_ms: Optional[float] = None) -> Callable[[T], T]:
        """
        Decorator to monitor function performance.
        
        Args:
            threshold_ms: Log warning if execution exceeds this (milliseconds)
        """
        def decorator(func: T) -> T:
            threshold = (threshold_ms / 1000.0) if threshold_ms else self.performance_thresholds.get(func.__name__)
            
            if iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        if threshold and duration > threshold:
                            self._logger.warning(
                                f"{func.__name__} took {duration:.3f}s (threshold: {threshold:.3f}s)"
                            )
                        else:
                            self._logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                        
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        self._logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                        raise
                
                return async_wrapper  # type: ignore
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        if threshold and duration > threshold:
                            self._logger.warning(
                                f"{func.__name__} took {duration:.3f}s (threshold: {threshold:.3f}s)"
                            )
                        else:
                            self._logger.debug(f"{func.__name__} completed in {duration:.3f}s")
                        
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        self._logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
                        raise
                
                return sync_wrapper  # type: ignore
        
        return decorator
    
    # Runtime configuration
    def set_level(self, level: str):
        """Change log level at runtime."""
        self._logger.remove()
        self._logger.add(
            sys.stderr,
            level=level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[tool_name]}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
            )
        )
        self._logger.info(f"Log level changed to {level}")
    
    def set_pii_redaction(self, enabled: bool = True):
        """Enable or disable PII redaction at runtime."""
        self.enable_pii_redaction = enabled
        self._logger.info(f"PII redaction {'enabled' if enabled else 'disabled'}")
    
    # Testing utilities
    def capture(self) -> LogCapture:
        """Create a log capture context for testing."""
        return LogCapture()
    
    # Rate limiting decorator
    def rate_limit(self, max_calls: int, time_window: timedelta) -> Callable[[T], T]:
        """
        Decorator to rate limit function calls.
        
        Args:
            max_calls: Maximum calls allowed
            time_window: Time window for the limit
        """
        limiter = RateLimiter(max_calls, time_window)
        
        def decorator(func: T) -> T:
            if iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    if not limiter.should_allow(func.__name__):
                        self._logger.warning(f"Rate limit exceeded for {func.__name__}")
                        return None
                    return await func(*args, **kwargs)
                return async_wrapper  # type: ignore
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    if not limiter.should_allow(func.__name__):
                        self._logger.warning(f"Rate limit exceeded for {func.__name__}")
                        return None
                    return func(*args, **kwargs)
                return sync_wrapper  # type: ignore
        
        return decorator
    
    # Backward compatibility - delegate to loguru
    def __getattr__(self, name: str) -> Any:
        """Forward undefined attributes to the underlying loguru logger."""
        return getattr(self._logger, name)


# Keep the original debug_tool function for backward compatibility
def debug_tool(mcp_logger: MCPLogger, catch_exceptions: bool = True) -> Callable:
    """
    Decorator for comprehensive tool debugging. Handles both sync and async functions.
    
    Args:
        mcp_logger: An instance of MCPLogger.
        catch_exceptions: If True, catches exceptions and returns a JSON error.
                          If False, re-raises the exception.
    """
    def decorator(func: Callable) -> Callable:
        is_async = iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            log_context = {"args": args, "kwargs": kwargs}
            mcp_logger.debug(f"Calling tool '{func_name}' with context: {mcp_logger._safe_json_dumps(log_context)}")

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                mcp_logger.log_call(func_name, duration, result)
                return result
            except asyncio.CancelledError:
                duration = time.time() - start_time
                mcp_logger.warning(f"Tool '{func_name}' cancelled after {duration:.3f}s")
                raise
            except Exception as e:
                duration = time.time() - start_time
                error_id = mcp_logger.log_error(func_name, duration, e, log_context)
                if catch_exceptions:
                    return mcp_logger._safe_json_dumps({
                        "error": {
                            "id": error_id,
                            "type": type(e).__name__,
                            "message": str(e),
                            "tool": func_name,
                            "traceback": traceback.format_exc()
                        }
                    }, indent=2)
                else:
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            log_context = {"args": args, "kwargs": kwargs}
            mcp_logger.debug(f"Calling tool '{func_name}' with context: {mcp_logger._safe_json_dumps(log_context)}")

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                mcp_logger.log_call(func_name, duration, result)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_id = mcp_logger.log_error(func_name, duration, e, log_context)
                if catch_exceptions:
                    return mcp_logger._safe_json_dumps({
                        "error": {
                            "id": error_id,
                            "type": type(e).__name__,
                            "message": str(e),
                            "tool": func_name,
                            "traceback": traceback.format_exc()
                        }
                    }, indent=2)
                else:
                    raise

        return async_wrapper if is_async else sync_wrapper
    return decorator