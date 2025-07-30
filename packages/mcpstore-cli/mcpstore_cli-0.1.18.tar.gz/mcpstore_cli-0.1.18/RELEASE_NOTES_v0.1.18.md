# Release Notes - v0.1.18

## Bug Fixes

### 🐛 Fixed Claude Desktop JSON-RPC Communication Error
- Fixed "Unexpected token '🌐'" error when using Claude Desktop
- Removed console output that was interfering with JSON-RPC protocol
- Now properly handles stdio communication without non-JSON output

## Technical Details

### Problem
When running `mcpstore-cli run --url`, the following console.print statements were outputting to stdout:
```
🌐 Starting HTTP proxy...
📡 URL: http://...
```

This caused Claude Desktop to fail with JSON parsing errors:
```
Unexpected token '🌐', "🌐 Startin"... is not valid JSON
Unexpected token '📡', "📡 URL: ht"... is not valid JSON
```

### Solution
- Commented out console.print statements in the `_run` function when operating in URL mode
- The stdio-to-HTTP proxy now operates silently without interfering with JSON-RPC communication
- All logging is still available via the logger for debugging purposes

## Compatibility
- Fully compatible with Claude Desktop's JSON-RPC requirements
- No changes to API or command-line interface
- Backward compatible with all existing configurations

## Usage
URL-based installations continue to work as before:
```bash
# Install URL to Claude Desktop
mcpstore-cli install "http://localhost:8090/mcp/..." "ServerName" --client claude

# Run stdio-to-HTTP proxy (now without console output)
mcpstore-cli run --url "http://localhost:8090/mcp/..."
```