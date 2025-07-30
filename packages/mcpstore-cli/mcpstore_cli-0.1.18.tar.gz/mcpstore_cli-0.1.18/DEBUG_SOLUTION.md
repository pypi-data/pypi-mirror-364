# 解决 Claude Desktop "Fetch" 错误的方案

## 问题分析

错误信息 "Unexpected token '�'" 可能由以下原因导致：

1. **命名冲突**: "Fetch" 是浏览器内置的 API 名称，可能与 Claude 内部处理冲突
2. **uvx 启动输出**: uvx 在启动时可能输出一些 Claude 无法解析的字符

## 解决方案

### 方案 1: 更改服务器名称
避免使用 "Fetch" 作为服务器名称：
```bash
# 使用其他名称，如 "WebFetch", "HTTPFetch", "FetchServer" 等
uvx mcpstore-cli install "http://localhost:8090/mcp/ae1e98fa600a47055c0f4896" "WebFetch" --client claude
```

### 方案 2: 使用 npx 替代 uvx
修改配置文件，将 uvx 改为 npx：
```json
{
  "WebFetch": {
    "command": "npx",
    "args": [
      "mcpstore-cli@latest",
      "run",
      "--url",
      "http://localhost:8090/mcp/ae1e98fa600a47055c0f4896?client=claude"
    ],
    "env": {
      "npm_config_yes": "true"
    }
  }
}
```

### 方案 3: 添加静默标志
如果 uvx 支持静默模式，可以尝试添加：
```json
{
  "WebFetch": {
    "command": "uvx",
    "args": [
      "--quiet",
      "mcpstore-cli",
      "run",
      "--url",
      "http://localhost:8090/mcp/ae1e98fa600a47055c0f4896?client=claude"
    ]
  }
}
```

### 方案 4: 使用 Python 直接运行
如果已安装 mcpstore-cli：
```json
{
  "WebFetch": {
    "command": "python",
    "args": [
      "-m",
      "agentrix.cli",
      "run",
      "--url",
      "http://localhost:8090/mcp/ae1e98fa600a47055c0f4896?client=claude"
    ]
  }
}
```

## 测试步骤

1. 首先尝试更改名称（最简单）
2. 如果仍有问题，尝试使用 npx
3. 查看 Claude 的日志以获取更多信息

## 可能的根本原因

- uvx 在下载/安装包时的输出可能包含进度条或特殊字符
- Claude Desktop 可能对某些保留名称（如 Fetch）有特殊处理
- 字符编码问题（虽然配置文件本身看起来正常）