# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mcpstore-cli is a Python MCP (Model Context Protocol) server registry and proxy. It provides server discovery, installation, configuration and runtime management for AI agents. The project is published as "mcpstore-cli" on PyPI.

## Important Context

- **MCP SDK**: Uses the official MCP Python SDK (mcp>=1.0.0) from https://github.com/modelcontextprotocol/python-sdk
- **Reference Servers**: The MCP servers demo at https://github.com/modelcontextprotocol/servers provides implementation examples
- **Proxy Example**: The https://github.com/sparfenyuk/mcp-proxy repository offers a good proxy implementation reference
- **Package Naming**: Published as "mcpstore-cli" on PyPI
- **CLI Entry Point**: `mcpstore-cli` command (maps to `mcpstore_cli.cli:main_cli`)

## Development Commands

### Setup and Installation
```bash
# Install dependencies (uses uv for package management)
uv sync --all-extras

# Install development dependencies only
uv sync --extra dev

# Install in development mode
uv pip install -e .
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage  
pytest --cov=mcpstore_cli --cov-report=html

# Run specific test file
pytest tests/test_filename.py

# Run tests excluding slow tests
pytest -m "not slow"

# Test files (in project root)
python test_cli.py      # CLI integration tests
python test_sdk_proxy.py  # SDK proxy tests
```

### Code Quality
```bash
# Format code
black src tests

# Lint code
ruff check src tests

# Fix linting issues
ruff check src tests --fix

# Type checking
mypy src
```

### Build and Distribution
```bash
# Build package
python -m build

# Publish (development)
python scripts/publish.py

# Publish (production)
./publish.sh
```

## Architecture

### Core Components

1. **CLI Interface (`cli.py`)**: Main command-line interface using Typer
   - Entry point: `mcpmarket` command (defined in pyproject.toml)
   - Commands: search, install, uninstall, run, dev, build, playground, etc.

2. **Registry System (`core/registry.py`)**: 
   - Manages server discovery from central registry
   - Handles caching and server metadata
   - Supports search, filtering, and server information retrieval

3. **Server Manager (`core/server_manager.py`)**:
   - Handles server installation (NPM, PyPI, GitHub, Docker)
   - Manages server lifecycle and runtime
   - Implements proxy mode for MCP communication

4. **Configuration Manager (`core/config.py`)**:
   - Manages client configurations (Cursor, Claude Desktop, VS Code)
   - Handles JSON/TOML config file operations
   - Supports backup and restore operations

5. **MCP Proxy (`core/mcp_proxy.py` and `core/mcp_sdk_proxy.py`)**:
   - Core proxy functionality for MCP protocol
   - Two implementations: direct JSON-RPC proxy and SDK-based proxy
   - Transparent communication between clients and servers
   - Handles server process management
   - SDK proxy uses official MCP Python SDK for better compatibility

### Key Design Patterns

**Proxy Architecture**: Mcpstore-cli uses a proxy pattern where:
- MCP clients are configured to run `mcpstore-cli run <server-id>`
- Mcpstore-cli receives the request and starts the target MCP server
- All MCP communication is transparently forwarded
- New SDK-based proxy provides better compatibility with official MCP protocol

**Server Types**: Supports multiple server distribution methods:
- `NPM`: JavaScript/Node.js packages via npx
- `PYPI`: Python packages via uvx
- `GITHUB`: Git repositories (cloned locally)
- `DOCKER`: Docker containers

**Configuration Flow**:
1. Client config files are read/written (JSON/TOML)
2. Server configurations are injected with proxy commands
3. Environment variables and API keys are managed automatically

### Additional Components

6. **Dev Server (`core/dev_server.py`)**:
   - Local development server for testing MCP servers
   - Hot reload support for development
   - Debugging capabilities

7. **Playground (`core/playground.py`)**:
   - Interactive testing environment for MCP servers
   - Real-time communication testing
   - Protocol debugging

8. **Inspector (`core/inspector.py`)**:
   - MCP server inspection and debugging tools
   - Protocol analysis capabilities

9. **HTTP Proxy (`core/http_proxy.py`)**:
   - Stdio-to-HTTP proxy for Claude Desktop
   - Enables Claude to access HTTP MCP servers
   - Transparent protocol translation

### Data Models

Located in `models/` directory:
- `config.py`: Configuration classes (McpstoreConfig, ClientConfig, etc.)
- `server.py`: Server-related models (ServerInfo, ServerConfig, ServerInstance)

## Common Development Patterns

### Adding New Commands
1. Add command function to `cli.py` with `@app.command()` decorator
2. Create async implementation function (e.g., `_command_name`)
3. Add error handling and logging
4. Update help text and examples

### Server Type Support
To add a new server type:
1. Add enum value to `ServerType` in `models/server.py`
2. Implement installation logic in `server_manager.py`
3. Add command building logic in `_build_server_command`
4. Update registry search and filtering

### Client Configuration
To add a new MCP client:
1. Add client configuration to `McpstoreConfig.get_default_client_configs()`
2. Ensure config format (JSON/TOML) is supported
3. Test configuration read/write operations

## CLI 命令参考

### 基础命令
- `mcpstore-cli search [query]` - 搜索 MCP 服务器
- `mcpstore-cli info <server-id>` - 查看服务器详情
- `mcpstore-cli install <server-id>` - 安装服务器到客户端
- `mcpstore-cli install <url> <name> --client <client>` - 安装 URL 类型的服务器
- `mcpstore-cli uninstall <server-id>` - 卸载服务器
- `mcpstore-cli list` - 列出已安装的服务器
- `mcpstore-cli run <server-id>` - 以代理模式运行服务器
- `mcpstore-cli run --url <url> <name>` - 运行 stdio-to-HTTP 代理

### 开发命令
- `mcpstore-cli dev <path>` - 启动开发服务器
- `mcpstore-cli build <path>` - 构建服务器包
- `mcpstore-cli playground` - 启动测试环境
- `mcpstore-cli inspect <server-id>` - 检查服务器协议

## 关键入口点

- **主 CLI**: `mcpstore_cli.cli:main_cli` (在 pyproject.toml 中定义为 `mcpstore-cli`)
- **配置加载**: `cli.py` 中的 `get_config()` 
- **服务器代理**: `server_manager.py` 中的 `run_server_proxy()`
- **注册表操作**: `ServerRegistry` 类方法

## 配置文件

- 主配置: `~/.mcpstore/config.toml`
- 客户端配置: 各种路径（参见 `example.config.toml`）
- 缓存: `~/.mcpstore/cache/servers.json`

## 开发与生产模式

- 开发模式: `config.dev_mode = True`
- 调试日志: `config.debug = True`
- 注册表 URL: 通过 `config.registry.url` 配置
- 默认注册表: https://registry.mcpstore.dev

## 测试策略

- 核心功能的单元测试
- 服务器安装/管理的集成测试
- 使用 pytest-asyncio 支持异步测试
- 使用 pytest-cov 进行覆盖率报告
- 慢速测试标记为 `@pytest.mark.slow`

## 环境变量

- `MCPSTORE_REGISTRY_URL` - 注册表 URL
- `MCPSTORE_API_KEY` - API 密钥
- `MCPSTORE_CONFIG_DIR` - 配置目录路径
- `MCPSTORE_CACHE_DIR` - 缓存目录路径

## URL 安装功能

### 概述
mcpstore-cli 支持安装 HTTP URL 类型的 MCP 服务器，并为 Claude Desktop 提供 stdio-to-HTTP 代理功能。

### 使用示例

```bash
# 安装 URL 到 Claude Desktop（生成 stdio 代理配置）
mcpstore-cli install "http://localhost:8090/mcp/75d341c4930b6662da822254?client=claude" "Gmail" --client claude

# 安装 URL 到 Cursor（生成直接 URL 配置）
mcpstore-cli install "http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor" "Gmail" --client cursor

# 手动运行 stdio-to-HTTP 代理
mcpstore-cli run --url "http://localhost:8090/mcp/75d341c4930b6662da822254" "Gmail"
```

### 配置格式差异

**Claude Desktop (claude_desktop_config.json)**:
```json
{
  "mcpServers": {
    "Gmail": {
      "command": "uvx",
      "args": [
        "mcpstore-cli",
        "run",
        "--url",
        "http://localhost:8090/mcp/75d341c4930b6662da822254?client=claude",
        "Gmail"
      ]
    }
  }
}
```

**Cursor**:
```json
{
  "mcpServers": {
    "Gmail": {
      "url": "http://localhost:8090/mcp/75d341c4930b6662da822254?client=cursor"
    }
  }
}
```