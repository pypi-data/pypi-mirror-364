"""
Stdio-to-HTTP proxy for MCP servers.

This module provides a proxy that receives MCP requests via stdio
and forwards them to HTTP MCP servers, enabling Claude Desktop
to communicate with HTTP-based MCP servers.
"""

import asyncio
import sys
from typing import List, Optional, Dict, Any

import anyio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

from ..utils.logger import get_logger

logger = get_logger(__name__)


class StdioToHttpProxy:
    """Proxy that bridges stdio MCP requests to streamable HTTP MCP servers."""
    
    def __init__(self, http_url: str, server_name: str):
        """
        Initialize the stdio-to-HTTP proxy.
        
        Args:
            http_url: The HTTP URL of the MCP server
            server_name: The name of the server
        """
        self.http_url = http_url
        self.server_name = server_name
        self.client_session: Optional[ClientSession] = None
        self.client_cm = None
        self._initialized = False
        
        logger.info(f"Initializing stdio-to-HTTP proxy for {server_name} at {http_url}")
    
    async def start(self):
        """Start the HTTP client connection"""
        logger.info(f"Connecting to HTTP server: {self.http_url}")
        self.client_cm = streamablehttp_client(self.http_url)
        read_stream, write_stream, get_session_id = await self.client_cm.__aenter__()
        
        # Create client session
        session = ClientSession(read_stream, write_stream)
        self.client_session = await session.__aenter__()
        logger.info("Client session created, deferring initialization")
    
    async def stop(self):
        """Stop the HTTP client connection"""
        if self.client_session:
            await self.client_session.__aexit__(None, None, None)
        if self.client_cm:
            await self.client_cm.__aexit__(None, None, None)
        self.client_cm = None
        self.client_session = None
    
    async def _ensure_initialized(self):
        """Ensure the client session is initialized"""
        if not self._initialized and self.client_session:
            logger.info("Initializing client session on first use...")
            try:
                await self.client_session.initialize()
                self._initialized = True
                logger.info("Client session initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize client session: {e}")
                raise
    
    async def list_tools(self) -> List[types.Tool]:
        """Forward list_tools request to target server"""
        try:
            await self._ensure_initialized()
            response = await self.client_session.list_tools()
            return response.tools
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> List[types.ContentBlock]:
        """Forward call_tool request to target server"""
        try:
            response = await self.client_session.call_tool(name, arguments or {})
            return response.content
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def list_resources(self) -> List[types.Resource]:
        """Forward list_resources request to target server"""
        try:
            await self._ensure_initialized()
            response = await self.client_session.list_resources()
            return response.resources
        except Exception as e:
            if "Method not found" in str(e):
                logger.info("Target server does not support resources")
            else:
                logger.error(f"Error listing resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> List[types.ContentBlock]:
        """Forward read_resource request to target server"""
        try:
            response = await self.client_session.read_resource(uri)
            return response.contents
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def list_prompts(self) -> List[types.Prompt]:
        """Forward list_prompts request to target server"""
        try:
            await self._ensure_initialized()
            response = await self.client_session.list_prompts()
            return response.prompts
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []
    
    async def get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
        """Forward get_prompt request to target server"""
        try:
            response = await self.client_session.get_prompt(name, arguments)
            return response
        except Exception as e:
            logger.error(f"Error getting prompt {name}: {e}")
            return types.GetPromptResult(
                description=f"Error: {str(e)}",
                messages=[]
            )
    
    async def run(self):
        """Run the stdio proxy server."""
        # Create the MCP server
        app = Server(self.server_name)
        
        # Register handlers
        @app.list_tools()
        async def list_tools() -> List[types.Tool]:
            return await self.list_tools()
        
        @app.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[types.ContentBlock]:
            return await self.call_tool(name, arguments)
        
        @app.list_resources()
        async def list_resources() -> List[types.Resource]:
            return await self.list_resources()
        
        @app.read_resource()
        async def read_resource(uri: str) -> List[types.ContentBlock]:
            return await self.read_resource(uri)
        
        @app.list_prompts()
        async def list_prompts() -> List[types.Prompt]:
            return await self.list_prompts()
        
        @app.get_prompt()
        async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> types.GetPromptResult:
            return await self.get_prompt(name, arguments)
        
        # Start the proxy connection to target server
        await self.start()
        
        try:
            # Run the stdio server
            logger.info(f"Starting stdio server for {self.server_name}")
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
        finally:
            # Clean up proxy connection
            await self.stop()


async def run_http_proxy(http_url: str, server_name: str):
    """
    Run the stdio-to-HTTP proxy.
    
    Args:
        http_url: The HTTP URL of the MCP server
        server_name: The name of the server
    """
    proxy = StdioToHttpProxy(http_url, server_name)
    await proxy.run()