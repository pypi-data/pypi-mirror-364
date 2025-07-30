# Release Notes - v0.1.17

## Improvements

### 🎨 Cleaner and More Consistent Output
- Removed verbose debug logs from user-facing output
- Unified all messages with emoji prefixes
- Cleaner installation flow with less clutter

### 📦 Installation Output Changes

#### Before (v0.1.16):
```
[14:39:14] INFO     Auto-appended client parameter:                                         cli.py:234
                    http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor                  
🔍 Validating URL: http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor...
⚠️  Warning: URL returned status 406
           INFO     Installing server 'Time' to client 'cursor'                           config.py:99
           INFO     Successfully installed 'Time' to 'cursor'                            config.py:123
✅ Server 'Time' installed to cursor

🎉 Successfully installed 'Time' to cursor!
💡 Restart cursor to use the new server
```

#### After (v0.1.17):
```
📦 Installing 'Time' to cursor...
✅ Successfully configured 'Time' in cursor
🎉 Installation complete!
💡 Restart cursor to use the new server
```

### 🐛 Bug Fixes
- Removed misleading 406 error warning (this is expected behavior for streamable HTTP servers)
- Removed redundant validation output that added no value

## Technical Details
- Debug logs are still available with `--verbose` flag if needed
- 406 errors during validation are expected for streamable HTTP MCP servers
- The actual connection uses proper streamablehttp_client which handles the protocol correctly

## User Experience
- Cleaner, more professional output
- Consistent emoji-based messaging
- Focus on what matters to the user