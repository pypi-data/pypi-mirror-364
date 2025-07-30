# Release Notes - v0.1.15

## Bug Fixes

### 🐛 Fixed Streamable HTTP Support
- Fixed HTTP proxy to support streamable HTTP MCP servers
- Resolved "Not Acceptable: Client must accept both application/json and text/event-stream" error
- Now correctly uses `streamablehttp_client` from MCP SDK

## Technical Changes

### HTTP Proxy Improvements
- Replaced httpx-based implementation with MCP SDK's streamablehttp_client
- Implemented proper ClientSession management
- Added deferred initialization pattern
- Better error handling for unsupported methods

### Before (v0.1.14):
- Used plain HTTP requests with httpx
- Only supported application/json content type
- Failed with 406 errors on streamable HTTP servers

### After (v0.1.15):
- Uses MCP SDK's streamablehttp_client
- Supports both application/json and text/event-stream
- Works with modern MCP HTTP servers

## Testing

Tested successfully with:
- Claude Desktop MCP Inspector
- Real MCP HTTP servers at localhost:8090

## Usage

No changes to usage - commands remain the same:

```bash
# Install URL-based server to Claude Desktop
mcpstore-cli install "http://localhost:8090/mcp/75d341c4930b6662da822254" "Time" --client claude

# Run stdio-to-HTTP proxy
mcpstore-cli run --url "http://localhost:8090/mcp/75d341c4930b6662da822254"
```

## Dependencies

No new dependencies - uses existing mcp package's streamablehttp_client module.