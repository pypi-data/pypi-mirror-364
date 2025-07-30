#!/bin/bash
# 快速发布脚本 - 直接发布到 PyPI

set -e

# 从 ~/.pypirc 文件加载认证信息
if [ -f "$HOME/.pypirc" ]; then
    export UV_PUBLISH_USERNAME=__token__
    export UV_PUBLISH_PASSWORD=$(grep "password" "$HOME/.pypirc" | grep -A1 "\[pypi\]" | tail -1 | cut -d'=' -f2 | xargs)
    echo "✅ 从 ~/.pypirc 文件加载认证信息"
else
    echo "❌ 错误: 未找到 ~/.pypirc 文件"
    exit 1
fi

echo "🚀 发布 mcpstore-cli 到 PyPI..."

# 直接发布
uv publish

if [ $? -eq 0 ]; then
    echo "✅ 成功发布到 PyPI!"
    echo "🔍 请访问: https://pypi.org/project/mcpstore-cli/"
    echo ""
    echo "📦 测试安装:"
    echo "uvx --no-cache mcpstore-cli install --help"
else
    echo "❌ 发布失败"
    exit 1
fi