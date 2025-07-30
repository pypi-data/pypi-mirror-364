#!/bin/bash
# MCP Feedback Enhanced 快速启动脚本

echo "🚀 MCP Feedback Enhanced 快速启动脚本"
echo "======================================"

# 检查 Python 版本
echo "🐍 检查 Python 版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 未安装或不在 PATH 中"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    echo "请运行: cd /Users/guoyansheng/vscodeProjects/mcp-feedback-enhanced"
    exit 1
fi

echo "✅ 在正确的项目目录中"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 激活虚拟环境失败"
    exit 1
fi
echo "✅ 虚拟环境已激活"

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip > /dev/null 2>&1

# 安装依赖
echo "📦 安装项目依赖..."
pip install -e . > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️ 项目安装失败，尝试手动安装依赖..."
    pip install fastmcp mcp psutil fastapi uvicorn jinja2 websockets aiohttp
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi
echo "✅ 依赖安装完成"

# 测试导入
echo "🧪 测试模块导入..."
python3 -c "
try:
    from mcp.types import ImageContent, TextContent
    from fastmcp import FastMCP
    import interactive_mcp_server
    print('✅ 所有模块导入成功')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ 模块导入测试失败"
    echo "请检查依赖安装"
    exit 1
fi

# 运行简单测试
if [ -f "simple_test.py" ]; then
    echo "🧪 运行序列化测试..."
    python3 simple_test.py > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ 图片序列化测试通过"
    else
        echo "⚠️ 序列化测试失败，但服务器仍可启动"
    fi
fi

echo ""
echo "🎉 准备工作完成！"
echo "======================================"
echo ""

# 询问是否启动服务器
read -p "是否现在启动 MCP 服务器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动 MCP Feedback Enhanced 服务器..."
    echo "按 Ctrl+C 停止服务器"
    echo ""
    
    # 启用调试模式
    export MCP_DEBUG=true
    
    # 启动服务器
    python3 -m mcp_feedback_enhanced
else
    echo ""
    echo "📝 手动启动命令："
    echo "source venv/bin/activate"
    echo "python3 -m mcp_feedback_enhanced"
    echo ""
    echo "或者启用调试模式："
    echo "MCP_DEBUG=true python3 -m mcp_feedback_enhanced"
fi
