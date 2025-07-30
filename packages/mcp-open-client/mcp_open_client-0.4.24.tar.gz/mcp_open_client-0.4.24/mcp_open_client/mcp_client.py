import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional, Union, Callable
from fastmcp import Client
from fastmcp.exceptions import McpError, ClientError
import mcp.types
import traceback
from .termux_workaround import apply_termux_workaround, setup_termux_environment, is_termux, is_android

logger = logging.getLogger(__name__)

# Type alias for progress handler
ProgressHandler = Callable[[float, str], None]

class McpClientError(Exception):
    """Custom exception for MCP client errors."""
    pass

class MCPClientManager:
    """
    Manager for MCP clients that handles connections to multiple MCP servers
    based on the configuration. Follows FastMCP best practices from reporte.md.
    """
    
    def __init__(self):
        self.client = None
        self.active_servers = {}
        self.config = {}
        self._initializing = False  # Flag to prevent concurrent initializations
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the MCP client with the given configuration."""
        # Prevent concurrent initializations
        if self._initializing:
            return False
        
        try:
            self._initializing = True
            
            # Apply Termux workaround if needed
            if is_termux() or is_android():
                setup_termux_environment()
                config = apply_termux_workaround(config)
            
            self.config = config
            
            
            # Create a new client with the current configuration
            if "mcpServers" in config and config["mcpServers"]:
                # Use all configured servers (no disabled filtering)
                active_servers = {}
                for name, server_config in config["mcpServers"].items():
                    # Create a clean copy without any 'disabled' field
                    clean_config = {k: v for k, v in server_config.items() if k != "disabled"}
                    active_servers[name] = clean_config
                
                if active_servers:
                    self.active_servers = active_servers
                    
                    # Use FastMCP's standard MCP configuration format
                    mcp_config = {"mcpServers": active_servers}
                    
                    try:
                        # Create the client - FastMCP handles all transport logic automatically
                        # FastMCP 2.8.1+ has fixed STDIO transport issues
                        self.client = Client(mcp_config)
                        
                        return True
                        
                    except Exception as e:
                        traceback.print_exc()
                        return False
                else:
                    return False
            else:
                return False
        except Exception as e:
            traceback.print_exc()
            return False
        finally:
            self._initializing = False

    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self.client is not None

    def is_connected(self) -> bool:
        """Check if the client is connected (same as initialized for FastMCP)."""
        return self.client is not None
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get the status of all configured servers."""
        return {
            "initialized": self.is_initialized(),
            "connected": self.is_connected(),
            "active_servers": list(self.active_servers.keys()) if self.active_servers else [],
            "total_servers": len(self.active_servers) if self.active_servers else 0
        }

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get all capabilities from all servers in a single session.
        This follows the best practice of using one session for multiple operations.
        """
        if not self.client:
            raise ValueError("MCP client not initialized")
        
        try:
            print("Getting all capabilities from MCP servers...")
            
            # Single session for multiple operations - CORRECT pattern from reporte.md
            async with self.client as client:
                # Get all capabilities in one session
                tools = await client.list_tools()
                resources = await client.list_resources()
                prompts = await client.list_prompts()
                
                return {
                    "tools": [{"name": t.name, "description": getattr(t, 'description', '')} for t in tools],
                    "resources": [{"uri": r.uri, "name": getattr(r, 'name', '')} for r in resources],
                    "prompts": [{"name": p.name, "description": getattr(p, 'description', '')} for p in prompts]
                }
                
        except Exception as e:
            traceback.print_exc()
            raise

    async def execute_operations(self, operations: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute multiple operations in a single session.
        This is the CORRECT pattern according to reporte.md.
        
        operations: List of operations, each with 'type' and operation-specific parameters
        Example:
        [
            {"type": "list_tools"},
            {"type": "call_tool", "name": "weather_get_forecast", "params": {"city": "London"}},
            {"type": "list_resources"}
        ]
        """
        if not self.client:
            raise ValueError("MCP client not initialized")
        
        results = []
        
        try:
            
            # Single session for ALL operations - CORRECT pattern
            async with self.client as client:
                for i, operation in enumerate(operations):
                    op_type = operation.get("type")
                    
                    try:
                        if op_type == "list_tools":
                            result = await client.list_tools()
                            results.append([{
                                "name": t.name,
                                "description": getattr(t, 'description', ''),
                                "inputSchema": getattr(t, 'inputSchema', None)
                            } for t in result])
                        
                        elif op_type == "list_resources":
                            result = await client.list_resources()
                            results.append([{"uri": r.uri, "name": getattr(r, 'name', '')} for r in result])
                        
                        elif op_type == "list_prompts":
                            result = await client.list_prompts()
                            results.append([{"name": p.name, "description": getattr(p, 'description', '')} for p in result])
                        
                        elif op_type == "call_tool":
                            tool_name = operation.get("name")
                            params = operation.get("params", {})
                            result = await client.call_tool(tool_name, params)
                            
                            # Normalize result to ensure consistent format across FastMCP versions
                            if hasattr(result, 'content'):
                                # CallToolResult object - extract content
                                normalized_result = result.content if result.content else []
                            else:
                                # Direct list or other format
                                normalized_result = result if result else []
                            
                            results.append(normalized_result)
                        
                        elif op_type == "read_resource":
                            uri = operation.get("uri")
                            result = await client.read_resource(uri)
                            results.append(result)
                        
                        elif op_type == "get_prompt":
                            name = operation.get("name")
                            arguments = operation.get("arguments", {})
                            result = await client.get_prompt(name, arguments)
                            results.append(result)
                        
                        else:
                            raise ValueError(f"Unknown operation type: {op_type}")
                            
                    except Exception as e:
                        results.append({"error": str(e), "operation": operation})
                
                return results
                
        except Exception as e:
            traceback.print_exc()
            raise

    # Convenience methods that use the correct pattern
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools. Uses single operation for simplicity."""
        operations = [{"type": "list_tools"}]
        results = await self.execute_operations(operations)
        return results[0] if results else []

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> List[Any]:
        """Call a tool. Uses single operation for simplicity."""
        operations = [{"type": "call_tool", "name": tool_name, "params": params}]
        results = await self.execute_operations(operations)
        return results[0] if results else []

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources. Uses single operation for simplicity."""
        operations = [{"type": "list_resources"}]
        results = await self.execute_operations(operations)
        return results[0] if results else []

    async def read_resource(self, uri: str) -> List[Any]:
        """Read a resource. Uses single operation for simplicity."""
        operations = [{"type": "read_resource", "uri": uri}]
        results = await self.execute_operations(operations)
        return results[0] if results else []

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts. Uses single operation for simplicity."""
        operations = [{"type": "list_prompts"}]
        results = await self.execute_operations(operations)
        return results[0] if results else []

    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> List[Any]:
        """Get a prompt. Uses single operation for simplicity."""
        operations = [{"type": "get_prompt", "name": name, "arguments": arguments or {}}]
        results = await self.execute_operations(operations)
        return results[0] if results else []
        
    async def generate_response(self, context: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Generate a response from the LLM using the provided context.
        
        Args:
            context: Dictionary containing message, tools, and resources
            
        Returns:
            Response from the LLM (string or dictionary with tool calls)
        """
        if not self.client:
            raise ValueError("MCP client not initialized")
            
        try:
            # Get the first active server
            server_names = self.get_server_names()
            if not server_names:
                raise ValueError("No active MCP servers available")
                
            server_name = server_names[0]
            
            # Extract the message from the context
            message = context.get("message", "")
            if not message:
                raise ValueError("No message provided in context")
                
            # Get the conversation history if available
            messages = context.get("messages", [])
            
            # Use the FastMCP client to generate a response
            async with self.client as client:
                # Call the LLM with the message and any available tools
                response = await client.call_tool(
                    "llm_generate",
                    {
                        "messages": messages if messages else [{"role": "user", "content": message}],
                        "tools": context.get("tools", []),
                        "resources": context.get("resources", []),
                        "options": context.get("options", {})
                    }
                )
                
                return response
                
        except Exception as e:
            traceback.print_exc()
            raise McpClientError(f"Error generating response: {str(e)}") from e

    def get_active_servers(self) -> Dict[str, Any]:
        """Get active servers configuration."""
        return self.active_servers.copy()

    def get_server_names(self) -> List[str]:
        """Get list of active server names."""
        return list(self.active_servers.keys())

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()

    async def close(self):
        """Close the client if needed."""
        # FastMCP handles cleanup automatically
        # No manual session management needed
        pass

# Create a singleton instance
mcp_client_manager = MCPClientManager()