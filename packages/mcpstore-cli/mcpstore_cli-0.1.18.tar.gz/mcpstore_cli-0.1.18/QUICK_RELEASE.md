# 快速发布指南 - v0.1.13

## 发布前检查清单

- [x] 更新版本号 (src/agentrix/__init__.py) → 0.1.13
- [x] 创建发布说明 (RELEASE_NOTES.md)
- [ ] 运行本地测试
- [ ] 提交代码到 Git
- [ ] 发布到 PyPI

## 发布步骤

### 1. 运行本地测试（可选）
```bash
# 测试新功能
python test_http_proxy.py

# 运行基本测试
python test_cli.py
```

### 2. 提交代码（如果使用 Git）
```bash
git add .
git commit -m "feat: add URL installation and stdio-to-HTTP proxy support"
git push
```

### 3. 发布到 PyPI

#### 方法 A: 使用自动脚本（推荐）
```bash
./publish.sh
```

#### 方法 B: 手动发布
```bash
# 清理旧构建
rm -rf build/ dist/ *.egg-info/

# 构建
uv build

# 发布到 TestPyPI（可选）
uv publish --publish-url https://test.pypi.org/legacy/

# 发布到正式 PyPI
uv publish
```

### 4. 验证发布
```bash
# 等待几分钟让 PyPI 更新索引，然后测试安装
uvx mcpstore-cli --version

# 测试新功能
uvx mcpstore-cli install "http://localhost:8090/mcp/test" "TestServer" --client claude
```

## 发布后通知

发布成功后，用户可以通过以下方式使用新功能：

```bash
# 使用 uvx（推荐）
uvx mcpstore-cli install <url> <name> --client claude

# 或使用 pip
pip install --upgrade mcpstore-cli
mcpstore-cli install <url> <name> --client claude
```

## 注意事项

1. **PyPI Token**: 确保 ~/.pypirc 文件中有有效的 PyPI token
2. **版本号**: 确保版本号未被使用过（PyPI 不允许重复版本）
3. **网络**: 确保网络连接稳定
4. **依赖**: 新功能使用现有依赖，无需更新 pyproject.toml

## 故障排除

如果发布失败：
1. 检查 PyPI token 是否有效
2. 确认版本号是否已存在
3. 查看错误信息并相应处理
4. 如需帮助，查看 PUBLISH.md 详细指南