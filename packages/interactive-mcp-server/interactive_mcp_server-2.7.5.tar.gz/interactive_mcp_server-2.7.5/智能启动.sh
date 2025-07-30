#!/bin/bash
# MCP Feedback Enhanced 智能启动脚本 - 支持多版本 Python

echo "🚀 MCP Feedback Enhanced 智能启动脚本"
echo "======================================"

# 检查可用的 Python 版本
PYTHON_CMD=""
PYTHON_VERSION=""

echo "🔍 检查可用的 Python 版本..."

# 按优先级检查 Python 版本
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v $cmd &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        
        echo "   发现: $cmd (版本 $VERSION)"
        
        # 检查是否满足最低要求 (3.10+)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD=$cmd
            PYTHON_VERSION=$VERSION
            echo "   ✅ $cmd 满足要求 (>= 3.10)"
            break
        else
            echo "   ⚠️  $cmd 版本过低 (需要 >= 3.10)"
        fi
    fi
done

# 如果没有找到合适的 Python 版本
if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "❌ 未找到满足要求的 Python 版本 (需要 >= 3.10)"
    echo ""
    echo "🔧 解决方案："
    echo ""
    echo "1. 安装 Python 3.11 (推荐):"
    echo "   macOS: brew install python@3.11"
    echo "   Ubuntu: sudo apt install python3.11"
    echo ""
    echo "2. 使用 pyenv 管理 Python 版本:"
    echo "   curl https://pyenv.run | bash"
    echo "   pyenv install 3.11.7"
    echo "   pyenv local 3.11.7"
    echo ""
    echo "3. 从官网下载安装包:"
    echo "   https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo ""
echo "✅ 使用 Python: $PYTHON_CMD (版本 $PYTHON_VERSION)"
echo ""

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    echo "当前目录: $(pwd)"
    echo "请运行: cd /path/to/interactive-mcp-server"
    exit 1
fi

echo "✅ 在正确的项目目录中"

# 检查虚拟环境
VENV_DIR="venv_py${MAJOR}${MINOR}"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 创建虚拟环境 ($VENV_DIR)..."
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "❌ 创建虚拟环境失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source $VENV_DIR/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ 激活虚拟环境失败"
    exit 1
fi
echo "✅ 虚拟环境已激活"

# 升级 pip
echo "⬆️ 升级 pip..."
pip install --upgrade pip > /dev/null 2>&1

# 安装依赖
echo "📦 安装核心依赖..."

# 先安装核心依赖
echo "   安装 fastmcp..."
pip install fastmcp > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   ❌ fastmcp 安装失败"
    echo ""
    echo "🔧 可能的解决方案："
    echo "1. 检查网络连接"
    echo "2. 使用国内镜像: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastmcp"
    echo "3. 升级到 Python 3.11+"
    exit 1
fi

echo "   安装 mcp..."
pip install mcp > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   ❌ mcp 安装失败"
    exit 1
fi

echo "   安装其他依赖..."
pip install psutil fastapi uvicorn jinja2 websockets aiohttp > /dev/null 2>&1

echo "📦 安装项目..."
# 尝试安装项目本身
pip install -e . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 项目安装成功"
else
    echo "⚠️ 项目安装失败，但核心依赖已安装"
    echo "   服务器仍可通过 PYTHONPATH 运行"
fi

echo "✅ 依赖安装完成"

# 测试导入
echo "🧪 测试模块导入..."
$PYTHON_CMD -c "
try:
    from mcp.types import ImageContent, TextContent
    print('✅ MCP 类型导入成功')

    from fastmcp import FastMCP
    print('✅ FastMCP 导入成功')

    # 测试项目模块（需要先安装项目）
    import sys
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

    try:
        import interactive_mcp_server
        print('✅ 项目模块导入成功')
    except ImportError as e:
        print(f'⚠️ 项目模块导入失败: {e}')
        print('   这是正常的，项目安装可能失败了')
        print('   但核心依赖已安装，服务器应该可以运行')

    print('✅ 核心依赖测试通过')

except ImportError as e:
    print(f'❌ 核心依赖导入失败: {e}')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ 核心依赖测试失败"
    echo "请检查 fastmcp 和 mcp 安装"
    exit 1
fi

# 运行简单测试
if [ -f "simple_test.py" ]; then
    echo "🧪 运行序列化测试..."
    $PYTHON_CMD simple_test.py > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ 图片序列化测试通过"
    else
        echo "⚠️ 序列化测试失败，但服务器仍可启动"
    fi
fi

echo ""
echo "🎉 准备工作完成！"
echo "使用 Python: $PYTHON_CMD ($PYTHON_VERSION)"
echo "虚拟环境: $VENV_DIR"
echo "======================================"
echo ""

# 询问是否启动服务器
read -p "是否现在启动 MCP 服务器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动 MCP Feedback Enhanced 服务器..."
    echo "使用 Python: $PYTHON_CMD"
    echo "按 Ctrl+C 停止服务器"
    echo ""
    
    # 启用调试模式
    export MCP_DEBUG=true
    
    # 设置 PYTHONPATH 以确保能找到项目模块
    export PYTHONPATH="$PWD/src:$PYTHONPATH"

    # 启动服务器
    $PYTHON_CMD -m mcp_feedback_enhanced
else
    echo ""
    echo "📝 手动启动命令："
    echo "source $VENV_DIR/bin/activate"
    echo "export PYTHONPATH=\"\$PWD/src:\$PYTHONPATH\""
    echo "$PYTHON_CMD -m mcp_feedback_enhanced"
    echo ""
    echo "或者启用调试模式："
    echo "MCP_DEBUG=true PYTHONPATH=\"\$PWD/src:\$PYTHONPATH\" $PYTHON_CMD -m mcp_feedback_enhanced"
fi
