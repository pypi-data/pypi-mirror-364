# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 SWE Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
MCP Tools for SWE Agent.
Provides LangGraph-compatible tools for managing MCP server integration.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

from .mcp_integration import mcp_manager, initialize_mcp_integration, create_mcp_config_example

logger = logging.getLogger(__name__)


class MCPConfigurationTool:
    """Tool for managing MCP server configuration."""
    
    name = "mcp_configure_server"
    description = """Configure MCP (Model Context Protocol) servers for additional capabilities.
    
    This tool allows you to add, update, or manage external MCP servers that provide
    specialized tools like math calculations, weather data, database access, etc.
    
    Parameters:
    - action: 'add', 'update', 'enable', 'disable', 'list', 'test', or 'create_example'
    - server_name: Name of the server (required for most actions)
    - config: Server configuration dictionary (for add/update actions)
    """
    
    def invoke(self, action: str, server_name: str = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MCP configuration action."""
        try:
            return asyncio.run(self._async_invoke(action, server_name, config))
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _async_invoke(self, action: str, server_name: str = None, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Async implementation of MCP configuration."""
        
        if action == "create_example":
            example_path = create_mcp_config_example()
            return {
                "success": True,
                "message": f"Created example MCP configuration at {example_path}",
                "example_path": example_path
            }
        
        if action == "list":
            await mcp_manager.initialize_client()
            info = mcp_manager.get_server_info()
            return {
                "success": True,
                "server_info": info,
                "message": f"Found {len(info['enabled_servers'])} enabled servers with {info['total_tools']} tools"
            }
        
        if action == "test":
            if not server_name:
                return {"success": False, "error": "server_name required for test action"}
            
            await mcp_manager.initialize_client()
            result = await mcp_manager.test_server_connection(server_name)
            return result
        
        if action in ["add", "update"]:
            if not server_name or not config:
                return {"success": False, "error": "server_name and config required for add/update actions"}
            
            success = mcp_manager.update_server_config(server_name, config)
            if success:
                return {
                    "success": True,
                    "message": f"{'Added' if action == 'add' else 'Updated'} server '{server_name}'"
                }
            else:
                return {"success": False, "error": f"Failed to {action} server configuration"}
        
        if action in ["enable", "disable"]:
            if not server_name:
                return {"success": False, "error": "server_name required for enable/disable actions"}
            
            # Load current config
            current_config = await mcp_manager.load_configuration()
            if server_name not in current_config:
                return {"success": False, "error": f"Server '{server_name}' not found in configuration"}
            
            # Update enabled status
            current_config[server_name]["enabled"] = (action == "enable")
            success = mcp_manager.update_server_config(server_name, current_config[server_name])
            
            if success:
                return {
                    "success": True,
                    "message": f"{'Enabled' if action == 'enable' else 'Disabled'} server '{server_name}'"
                }
            else:
                return {"success": False, "error": f"Failed to {action} server"}
        
        return {"success": False, "error": f"Unknown action: {action}"}


class MCPToolInvocationTool:
    """Tool for invoking MCP server tools."""
    
    name = "mcp_invoke_tool"
    description = """Invoke tools from connected MCP servers.
    
    This tool allows you to execute functions provided by external MCP servers,
    such as math calculations, weather queries, database operations, etc.
    
    Parameters:
    - tool_name: Name of the MCP tool to invoke
    - tool_args: Dictionary of arguments to pass to the tool
    """
    
    def invoke(self, tool_name: str, tool_args: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute MCP tool invocation."""
        try:
            return asyncio.run(self._async_invoke(tool_name, tool_args or {}))
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _async_invoke(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Async implementation of MCP tool invocation."""
        try:
            # Ensure MCP integration is initialized
            await initialize_mcp_integration()
            
            if not mcp_manager.client:
                return {"success": False, "error": "No MCP servers are configured or enabled"}
            
            if not mcp_manager.mcp_tools:
                return {"success": False, "error": "No MCP tools available"}
            
            # Find and invoke the tool
            for tool in mcp_manager.mcp_tools:
                if hasattr(tool, 'name') and tool.name == tool_name:
                    result = await tool.ainvoke(tool_args)
                    return {
                        "success": True,
                        "tool_name": tool_name,
                        "result": result,
                        "message": f"Successfully invoked MCP tool '{tool_name}'"
                    }
            
            # List available tools for reference
            available_tools = [
                tool.name if hasattr(tool, 'name') else str(tool) 
                for tool in mcp_manager.mcp_tools
            ]
            
            return {
                "success": False,
                "error": f"MCP tool '{tool_name}' not found",
                "available_tools": available_tools
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error invoking MCP tool: {str(e)}"}


class MCPStatusTool:
    """Tool for checking MCP server status and available tools."""
    
    name = "mcp_status"
    description = """Check status of MCP server integration and list available tools.
    
    This tool provides information about:
    - Connected MCP servers
    - Available tools from each server
    - Server connection status
    - Configuration details
    """
    
    def invoke(self) -> Dict[str, Any]:
        """Get MCP integration status."""
        try:
            return asyncio.run(self._async_invoke())
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _async_invoke(self) -> Dict[str, Any]:
        """Async implementation of MCP status check."""
        try:
            # Initialize if not already done
            await initialize_mcp_integration()
            
            # Get server info
            server_info = mcp_manager.get_server_info()
            
            # Get detailed tool information
            tool_details = []
            for tool in mcp_manager.mcp_tools:
                tool_info = {
                    "name": getattr(tool, 'name', 'unknown'),
                    "description": getattr(tool, 'description', 'No description available'),
                    "type": type(tool).__name__
                }
                tool_details.append(tool_info)
            
            return {
                "success": True,
                "server_info": server_info,
                "tools": tool_details,
                "message": f"MCP integration active with {len(server_info['enabled_servers'])} servers and {len(tool_details)} tools"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error checking MCP status: {str(e)}"}


# Create tool instances for LangGraph
mcp_configure_tool = MCPConfigurationTool()
mcp_invoke_tool = MCPToolInvocationTool()
mcp_status_tool = MCPStatusTool()

# Export tools for use in agent workflows
MCP_TOOLS = [
    mcp_configure_tool,
    mcp_invoke_tool,
    mcp_status_tool
]