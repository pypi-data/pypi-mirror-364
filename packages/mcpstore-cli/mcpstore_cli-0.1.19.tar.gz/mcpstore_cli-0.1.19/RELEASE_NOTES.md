# Release Notes

## Version 0.1.19 (Latest)

### Major Changes
- **Complete Refactoring**: Renamed entire project from `agentrix` to `mcpstore-cli`
- **Removed External Dependencies**: Removed all references to `@smithery/cli`
- **Project Structure Updates**: Configuration directory changed from `~/.agentrix/` to `~/.mcpstore/`

### Breaking Changes
- Configuration files now use `~/.mcpstore/` directory
- Environment variable prefix changed from `AGENTRIX_` to `MCPSTORE_`

---

## Version 0.1.18

### Bug Fixes
- Fixed Claude Desktop JSON-RPC communication error ("Unexpected token '🌐'")
- Removed console output that was interfering with stdio MCP protocol

### Technical Details
- Commented out console.print statements in URL mode to prevent JSON-RPC interference
- Stdio-to-HTTP proxy now operates silently for proper Claude Desktop compatibility

---

## Version 0.1.17

### Improvements
- Cleaner and more consistent output with emoji prefixes
- Removed verbose debug logs from user-facing output
- Fixed misleading 406 error warning for streamable HTTP servers

---

## Version 0.1.13

### New Features

#### 🌐 URL-based MCP Server Installation
- Added support for installing HTTP URL-based MCP servers
- New command format: `mcpstore-cli install <url> <name> --client <client>`
- Automatic URL validation during installation

#### 🔄 Stdio-to-HTTP Proxy
- Implemented stdio-to-HTTP proxy for Claude Desktop compatibility
- Claude Desktop can now access HTTP MCP servers through stdio interface
- New proxy module: `core/http_proxy.py`

#### 🎯 Intelligent Client Configuration
- Different configuration formats for different clients:
  - **Claude Desktop**: Generates stdio proxy command configuration
  - **Other clients (e.g., Cursor)**: Generates direct URL configuration
- Automatic client type detection

#### 🚀 Enhanced Run Command
- Added `--url` parameter to run command
- Direct HTTP proxy execution: `mcpstore-cli run --url <url> <name>`

### Usage Examples

```bash
# Install URL to Claude Desktop (generates stdio proxy config)
uvx mcpstore-cli install "http://localhost:8090/mcp/abc123?client=claude" "Gmail" --client claude

# Install URL to Cursor (generates direct URL config)
uvx mcpstore-cli install "http://localhost:8090/mcp/abc123?client=cursor" "Gmail" --client cursor

# Run stdio-to-HTTP proxy manually
uvx mcpstore-cli run --url "http://localhost:8090/mcp/abc123" "Gmail"
```