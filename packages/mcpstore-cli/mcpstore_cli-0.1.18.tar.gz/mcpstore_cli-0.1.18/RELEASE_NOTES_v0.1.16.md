# Release Notes - v0.1.16

## New Features

### 🎯 Auto-append Client Query Parameter
- Automatically adds `?client=<client>` to URLs when using `install` command
- Intelligently detects if URL already contains client parameter
- Simplifies user experience - no need to manually add client parameter

## Usage Examples

### Before (v0.1.15):
```bash
# User had to manually add ?client=claude
mcpstore-cli install "http://localhost:8090/mcp/xxx?client=claude" "Time" --client claude
```

### After (v0.1.16):
```bash
# Client parameter is automatically added
mcpstore-cli install "http://localhost:8090/mcp/xxx" "Time" --client claude
# Results in: http://localhost:8090/mcp/xxx?client=claude

# If URL already has client parameter, it's preserved
mcpstore-cli install "http://localhost:8090/mcp/xxx?client=cursor" "Time" --client claude
# Results in: http://localhost:8090/mcp/xxx?client=cursor (unchanged)
```

## Technical Details

- Uses `urllib.parse` to properly handle URL query parameters
- Preserves existing query parameters
- Only adds client parameter if not already present
- Logs whether parameter was added or already existed

## Compatibility

- Fully backward compatible
- Works with all existing URL formats
- No changes to command syntax