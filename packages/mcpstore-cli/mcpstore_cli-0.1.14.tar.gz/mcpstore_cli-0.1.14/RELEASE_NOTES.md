# Release Notes - v0.1.13

## New Features

### 🌐 URL-based MCP Server Installation
- Added support for installing HTTP URL-based MCP servers
- New command format: `mcpstore-cli install <url> <name> --client <client>`
- Automatic URL validation during installation

### 🔄 Stdio-to-HTTP Proxy
- Implemented stdio-to-HTTP proxy for Claude Desktop compatibility
- Claude Desktop can now access HTTP MCP servers through stdio interface
- New proxy module: `core/http_proxy.py`

### 🎯 Intelligent Client Configuration
- Different configuration formats for different clients:
  - **Claude Desktop**: Generates stdio proxy command configuration
  - **Other clients (e.g., Cursor)**: Generates direct URL configuration
- Automatic client type detection

### 🚀 Enhanced Run Command
- Added `--url` parameter to run command
- Direct HTTP proxy execution: `mcpstore-cli run --url <url> <name>`

## Usage Examples

```bash
# Install URL to Claude Desktop (generates stdio proxy config)
uvx mcpstore-cli install "http://localhost:8090/mcp/abc123?client=claude" "Gmail" --client claude

# Install URL to Cursor (generates direct URL config)
uvx mcpstore-cli install "http://localhost:8090/mcp/abc123?client=cursor" "Gmail" --client cursor

# Run stdio-to-HTTP proxy manually
uvx mcpstore-cli run --url "http://localhost:8090/mcp/abc123" "Gmail"
```

## Generated Configurations

### Claude Desktop (stdio proxy)
```json
{
  "mcpServers": {
    "Gmail": {
      "command": "uvx",
      "args": [
        "mcpstore-cli",
        "run",
        "--url",
        "http://localhost:8090/mcp/abc123?client=claude",
        "Gmail"
      ]
    }
  }
}
```

### Cursor (direct URL)
```json
{
  "mcpServers": {
    "Gmail": {
      "url": "http://localhost:8090/mcp/abc123?client=cursor"
    }
  }
}
```

## Technical Details

- Full MCP protocol support (tools, resources, prompts)
- Error handling and retry logic
- Connection validation
- Transparent protocol translation
- Backward compatibility maintained

## Breaking Changes
None - all existing functionality remains intact.

## Bug Fixes
- Improved error messages for invalid configurations
- Better handling of network timeouts

## Dependencies
No new dependencies added. Uses existing `httpx` and `mcp` packages.