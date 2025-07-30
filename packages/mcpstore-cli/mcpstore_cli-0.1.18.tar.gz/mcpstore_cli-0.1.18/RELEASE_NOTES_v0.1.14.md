# Release Notes - v0.1.14

## Bug Fixes

### 🐛 Fixed URL-based Server Configuration
- Removed unnecessary server name parameter from Claude Desktop configuration
- Claude Desktop now correctly executes: `uvx mcpstore-cli run --url <url>`
- Previous version incorrectly added server name as an extra argument

## Configuration Changes

### Before (v0.1.13):
```json
{
  "mcpServers": {
    "Time": {
      "command": "uvx",
      "args": [
        "mcpstore-cli",
        "run",
        "--url",
        "http://localhost:8090/mcp/75d341c4930b6662da822254",
        "Time"  // <-- This was incorrect
      ]
    }
  }
}
```

### After (v0.1.14):
```json
{
  "mcpServers": {
    "Time": {
      "command": "uvx",
      "args": [
        "mcpstore-cli",
        "run",
        "--url",
        "http://localhost:8090/mcp/75d341c4930b6662da822254"
      ]
    }
  }
}
```

## Usage

The command syntax remains the same:

```bash
# Install URL-based server to Claude Desktop
mcpstore-cli install "http://localhost:8090/mcp/75d341c4930b6662da822254" "Time" --client claude

# Run stdio-to-HTTP proxy manually
mcpstore-cli run --url "http://localhost:8090/mcp/75d341c4930b6662da822254"
```

## Technical Details

- Updated `_generate_server_config` in `config.py` to generate correct args
- Updated `run` command to properly handle URL-only mode
- Server name is now extracted from URL path for proxy identification

## Compatibility

- Fully backward compatible with v0.1.13
- Existing configurations should be reinstalled with `--force` flag to apply the fix