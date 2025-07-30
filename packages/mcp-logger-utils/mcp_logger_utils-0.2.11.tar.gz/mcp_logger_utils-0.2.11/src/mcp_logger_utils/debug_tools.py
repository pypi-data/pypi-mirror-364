"""Debug tools for MCP servers - reload and instance management."""

import json
import os
import signal
import subprocess
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

import psutil


class MCPDebugTools:
    """Debug utilities for MCP server development."""
    
    def __init__(self, server_name: str, logger=None, auto_clear_cache: bool = True):
        """
        Initialize debug tools for an MCP server.
        
        Args:
            server_name: Name of the MCP server (e.g., 'mcp_youtube_transcripts')
            logger: Optional MCPLogger instance for logging
            auto_clear_cache: Whether to automatically clear UV cache on reload
        """
        self.server_name = server_name
        self.logger = logger
        self.current_pid = os.getpid()
        self.auto_clear_cache = auto_clear_cache
    
    def find_instances(self) -> List[Dict[str, Any]]:
        """
        Find all running instances of this MCP server.
        
        Returns:
            List of instance information dictionaries
        """
        instances = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Check if this is our MCP server
                if (self.server_name in cmdline_str and 
                    'src/cc_executor/servers/' in cmdline_str):
                    
                    # Get process start time
                    create_time = proc.info.get('create_time', 0)
                    start_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                             time.localtime(create_time))
                    
                    instances.append({
                        "pid": proc.info['pid'],
                        "is_current": proc.info['pid'] == self.current_pid,
                        "start_time": start_time,
                        "cmd": cmdline_str[:200] + "..." if len(cmdline_str) > 200 else cmdline_str
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(instances, key=lambda x: x['pid'])
    
    def clear_uv_cache(self) -> int:
        """
        Clear UV cache for this MCP server.
        
        Returns:
            Number of cache entries cleared
        """
        cleared = 0
        uv_cache_dir = Path.home() / ".cache" / "uv" / "environments-v2"
        
        if uv_cache_dir.exists():
            # Clear caches for this server
            patterns = [
                f"*{self.server_name}*",
                f"*{self.server_name.replace('mcp_', '')}*"
            ]
            
            for pattern in patterns:
                for cache_path in uv_cache_dir.glob(pattern):
                    try:
                        if cache_path.is_dir():
                            shutil.rmtree(cache_path)
                            cleared += 1
                            if self.logger:
                                self.logger.debug(f"Cleared UV cache: {cache_path.name}")
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"Failed to clear cache {cache_path}: {e}")
        
        # Also clear built wheels for mcp-logger-utils
        wheels_cache = Path.home() / ".cache" / "uv" / "built-wheels-v3"
        if wheels_cache.exists():
            for wheel_path in wheels_cache.glob("*mcp-logger-utils*"):
                try:
                    if wheel_path.is_dir():
                        shutil.rmtree(wheel_path)
                        cleared += 1
                except:
                    pass
        
        return cleared
    
    def kill_old_instances(self) -> List[int]:
        """
        Kill all old instances of this MCP server.
        
        Returns:
            List of PIDs that were killed
        """
        killed_pids = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Check if this is our MCP server (but not current instance)
                if (self.server_name in cmdline_str and 
                    proc.info['pid'] != self.current_pid and
                    'src/cc_executor/servers/' in cmdline_str):
                    
                    # Kill the old process
                    if self.logger:
                        self.logger.info(f"Killing old MCP server instance: PID {proc.info['pid']}")
                    
                    os.kill(proc.info['pid'], signal.SIGTERM)
                    killed_pids.append(proc.info['pid'])
                    
                    # Give it a moment to die
                    time.sleep(0.1)
                    
                    # Force kill if still alive
                    if psutil.pid_exists(proc.info['pid']):
                        os.kill(proc.info['pid'], signal.SIGKILL)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, ProcessLookupError):
                continue
        
        # Also try pkill as a backup
        try:
            subprocess.run(['pkill', '-f', f'{self.server_name}.py'], 
                         capture_output=True, text=True)
        except:
            pass
        
        return killed_pids
    
    async def debug_reload_server(self) -> str:
        """
        Kill all old instances and prepare for reload.
        
        Returns:
            JSON string with status information
        """
        try:
            killed_pids = self.kill_old_instances()
            
            # Clear UV cache if enabled
            cleared_caches = 0
            if self.auto_clear_cache:
                cleared_caches = self.clear_uv_cache()
            
            result = {
                "status": "success",
                "current_pid": self.current_pid,
                "killed_pids": killed_pids,
                "cleared_caches": cleared_caches,
                "message": f"Killed {len(killed_pids)} old instance(s), cleared {cleared_caches} cache(s). Current PID: {self.current_pid}",
                "next_step": "Reload Claude to connect to the updated MCP server"
            }
            
            if self.logger:
                self.logger.info(f"Debug reload completed: {result['message']}")
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "current_pid": self.current_pid,
                "error": str(e),
                "message": "Failed to kill old instances, but current server is running"
            }
            if self.logger:
                self.logger.error(f"Debug reload error: {e}")
            return json.dumps(error_result, indent=2)
    
    async def debug_list_instances(self) -> str:
        """
        List all running instances of this MCP server.
        
        Returns:
            JSON string with instance information
        """
        try:
            instances = self.find_instances()
            
            result = {
                "status": "success",
                "current_pid": self.current_pid,
                "instance_count": len(instances),
                "instances": instances,
                "message": f"Found {len(instances)} instance(s) of {self.server_name}"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            error_result = {
                "status": "error",
                "current_pid": self.current_pid,
                "error": str(e),
                "message": "Failed to list instances"
            }
            return json.dumps(error_result, indent=2)


def create_debug_tools(mcp_server, server_name: str, logger=None, auto_clear_cache: bool = None):
    """
    Helper function to add debug tools to an MCP server.
    
    Args:
        mcp_server: FastMCP server instance
        server_name: Name of the MCP server
        logger: Optional MCPLogger instance
        auto_clear_cache: Whether to clear UV cache on reload (defaults to True in debug mode)
        
    Example:
        from mcp_logger_utils import MCPLogger, create_debug_tools
        
        mcp = FastMCP("my-server")
        logger = MCPLogger("my-server")
        create_debug_tools(mcp, "my-server", logger)
    """
    # Default to auto-clearing cache in debug mode
    if auto_clear_cache is None:
        auto_clear_cache = os.getenv("MCP_DEBUG", "false").lower() == "true"
    
    debug_tools = MCPDebugTools(server_name, logger, auto_clear_cache)
    
    # Register the debug tools as MCP tools
    @mcp_server.tool()
    async def debug_reload_server() -> str:
        """Kill all old instances of this MCP server and prepare for reload."""
        return await debug_tools.debug_reload_server()
    
    @mcp_server.tool()
    async def debug_list_instances() -> str:
        """List all running instances of this MCP server."""
        return await debug_tools.debug_list_instances()
    
    @mcp_server.tool()
    async def debug_clear_cache() -> str:
        """Clear UV cache for this MCP server."""
        try:
            cleared = debug_tools.clear_uv_cache()
            return json.dumps({
                "status": "success",
                "cleared_entries": cleared,
                "message": f"Cleared {cleared} cache entries for {server_name}"
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "message": "Failed to clear cache"
            }, indent=2)
    
    return debug_tools