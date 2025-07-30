"""
Stdio-to-HTTP proxy for MCP servers.

This module provides a proxy that receives MCP requests via stdio
and forwards them to HTTP MCP servers, enabling Claude Desktop
to communicate with HTTP-based MCP servers.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import anyio
import httpx
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from ..utils.logger import get_logger

logger = get_logger(__name__)


class StdioToHttpProxy:
    """Proxy that bridges stdio MCP requests to HTTP MCP servers."""
    
    def __init__(self, http_url: str, server_name: str, timeout: float = 30.0):
        """
        Initialize the stdio-to-HTTP proxy.
        
        Args:
            http_url: The HTTP URL of the MCP server
            server_name: The name of the server
            timeout: Request timeout in seconds
        """
        self.http_url = http_url.rstrip('/')
        self.server_name = server_name
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None
        self._server_info: Optional[Dict[str, Any]] = None
        
        # Parse URL to extract base URL and any query parameters
        parsed = urlparse(http_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        self.query_params = parsed.query
        
        logger.info(f"Initializing stdio-to-HTTP proxy for {server_name} at {http_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"mcpstore-cli/stdio-http-proxy/{self.server_name}"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Make a JSON-RPC request to the HTTP server.
        
        Args:
            method: The JSON-RPC method name
            params: Optional parameters for the method
            
        Returns:
            The result from the JSON-RPC response
            
        Raises:
            Exception: If the request fails or returns an error
        """
        if not self.client:
            raise RuntimeError("HTTP client not initialized")
        
        # Prepare JSON-RPC request
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        logger.debug(f"Sending request to {self.http_url}: {method}")
        
        try:
            # Make the HTTP request
            url = self.http_url
            if self.query_params:
                url = f"{url}?{self.query_params}"
                
            response = await self.client.post(url, json=request_data)
            response.raise_for_status()
            
            # Parse JSON-RPC response
            result = response.json()
            
            if "error" in result:
                error = result["error"]
                raise Exception(f"JSON-RPC error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")
            
            return result.get("result")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"HTTP error {e.response.status_code}: Failed to communicate with MCP server")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Failed to connect to MCP server: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def _get_server_info(self) -> Dict[str, Any]:
        """Get server information (cached)."""
        if self._server_info is None:
            self._server_info = await self._make_request("initialize", {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcpstore-cli-proxy",
                    "version": "1.0.0"
                }
            })
        return self._server_info
    
    async def run(self):
        """Run the stdio proxy server."""
        async with self:
            # Create the MCP server
            app = Server(self.server_name)
            
            # Initialize handler
            @app.list_tools()
            async def list_tools() -> List[types.Tool]:
                """List available tools from the HTTP server."""
                try:
                    result = await self._make_request("tools/list")
                    tools = []
                    for tool_data in result.get("tools", []):
                        tools.append(types.Tool(
                            name=tool_data["name"],
                            description=tool_data.get("description", ""),
                            inputSchema=tool_data.get("inputSchema", {})
                        ))
                    return tools
                except Exception as e:
                    logger.error(f"Failed to list tools: {e}")
                    return []
            
            @app.call_tool()
            async def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[types.ContentBlock]:
                """Call a tool on the HTTP server."""
                try:
                    result = await self._make_request("tools/call", {
                        "name": name,
                        "arguments": arguments or {}
                    })
                    
                    content_blocks = []
                    for content in result.get("content", []):
                        if content["type"] == "text":
                            content_blocks.append(types.TextContent(
                                type="text",
                                text=content["text"]
                            ))
                        elif content["type"] == "image":
                            content_blocks.append(types.ImageContent(
                                type="image",
                                data=content["data"],
                                mimeType=content["mimeType"]
                            ))
                        elif content["type"] == "resource":
                            content_blocks.append(types.EmbeddedResource(
                                type="resource",
                                resource=types.Resource(
                                    uri=content["resource"]["uri"],
                                    name=content["resource"].get("name", ""),
                                    description=content["resource"].get("description"),
                                    mimeType=content["resource"].get("mimeType")
                                )
                            ))
                    
                    return content_blocks
                except Exception as e:
                    logger.error(f"Failed to call tool {name}: {e}")
                    return [types.TextContent(type="text", text=f"Error calling tool: {str(e)}")]
            
            @app.list_resources()
            async def list_resources() -> List[types.Resource]:
                """List available resources from the HTTP server."""
                try:
                    result = await self._make_request("resources/list")
                    resources = []
                    for res_data in result.get("resources", []):
                        resources.append(types.Resource(
                            uri=res_data["uri"],
                            name=res_data.get("name", ""),
                            description=res_data.get("description"),
                            mimeType=res_data.get("mimeType")
                        ))
                    return resources
                except Exception as e:
                    logger.error(f"Failed to list resources: {e}")
                    return []
            
            @app.read_resource()
            async def read_resource(uri: str) -> List[types.ContentBlock]:
                """Read a resource from the HTTP server."""
                try:
                    result = await self._make_request("resources/read", {"uri": uri})
                    
                    content_blocks = []
                    for content in result.get("contents", []):
                        if content["type"] == "text":
                            content_blocks.append(types.TextContent(
                                type="text",
                                text=content["text"]
                            ))
                        elif content["type"] == "blob":
                            content_blocks.append(types.BlobContent(
                                type="blob",
                                blob=content["blob"],
                                mimeType=content.get("mimeType", "application/octet-stream")
                            ))
                    
                    return content_blocks
                except Exception as e:
                    logger.error(f"Failed to read resource {uri}: {e}")
                    return [types.TextContent(type="text", text=f"Error reading resource: {str(e)}")]
            
            @app.list_prompts()
            async def list_prompts() -> List[types.Prompt]:
                """List available prompts from the HTTP server."""
                try:
                    result = await self._make_request("prompts/list")
                    prompts = []
                    for prompt_data in result.get("prompts", []):
                        prompts.append(types.Prompt(
                            name=prompt_data["name"],
                            description=prompt_data.get("description", ""),
                            arguments=[
                                types.PromptArgument(
                                    name=arg["name"],
                                    description=arg.get("description", ""),
                                    required=arg.get("required", False)
                                )
                                for arg in prompt_data.get("arguments", [])
                            ]
                        ))
                    return prompts
                except Exception as e:
                    logger.error(f"Failed to list prompts: {e}")
                    return []
            
            @app.get_prompt()
            async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
                """Get a prompt from the HTTP server."""
                try:
                    result = await self._make_request("prompts/get", {
                        "name": name,
                        "arguments": arguments or {}
                    })
                    
                    messages = []
                    for msg in result.get("messages", []):
                        content_blocks = []
                        for content in msg.get("content", []):
                            if content["type"] == "text":
                                content_blocks.append(types.TextContent(
                                    type="text",
                                    text=content["text"]
                                ))
                            elif content["type"] == "image":
                                content_blocks.append(types.ImageContent(
                                    type="image",
                                    data=content["data"],
                                    mimeType=content["mimeType"]
                                ))
                        
                        messages.append(types.PromptMessage(
                            role=msg["role"],
                            content=content_blocks
                        ))
                    
                    return types.GetPromptResult(
                        description=result.get("description", ""),
                        messages=messages
                    )
                except Exception as e:
                    logger.error(f"Failed to get prompt {name}: {e}")
                    return types.GetPromptResult(
                        description=f"Error getting prompt: {str(e)}",
                        messages=[]
                    )
            
            # Run the stdio server
            logger.info(f"Starting stdio server for {self.server_name}")
            try:
                async with stdio_server() as streams:
                    await app.run(
                        streams[0], 
                        streams[1], 
                        app.create_initialization_options()
                    )
            except KeyboardInterrupt:
                logger.info("Stdio server stopped by user")
            except Exception as e:
                logger.error(f"Stdio server error: {e}")
                raise


async def run_http_proxy(http_url: str, server_name: str):
    """
    Run the stdio-to-HTTP proxy.
    
    Args:
        http_url: The HTTP URL of the MCP server
        server_name: The name of the server
    """
    proxy = StdioToHttpProxy(http_url, server_name)
    await proxy.run()