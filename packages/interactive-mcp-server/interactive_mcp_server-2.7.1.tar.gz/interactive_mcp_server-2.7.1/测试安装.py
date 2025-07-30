#!/usr/bin/env python3
"""
测试 MCP Feedback Enhanced 安装
"""

import sys
import os

print("🧪 MCP Feedback Enhanced 安装测试")
print("=" * 40)

# 添加项目路径到 sys.path
project_src = os.path.join(os.path.dirname(__file__), 'src')
if os.path.exists(project_src):
    sys.path.insert(0, project_src)
    print(f"✅ 添加项目路径: {project_src}")

print(f"🐍 Python 版本: {sys.version}")
print(f"📁 当前目录: {os.getcwd()}")

# 测试核心依赖
print("\n🔧 测试核心依赖...")

try:
    from mcp.types import ImageContent, TextContent
    print("✅ mcp.types 导入成功")
except ImportError as e:
    print(f"❌ mcp.types 导入失败: {e}")
    sys.exit(1)

try:
    from fastmcp import FastMCP
    print("✅ fastmcp 导入成功")
except ImportError as e:
    print(f"❌ fastmcp 导入失败: {e}")
    sys.exit(1)

# 测试项目模块
print("\n📦 测试项目模块...")

try:
    import mcp_feedback_enhanced
    print("✅ mcp_feedback_enhanced 导入成功")
    
    # 测试主要模块
    from mcp_feedback_enhanced import server
    print("✅ server 模块导入成功")
    
    from mcp_feedback_enhanced.server import process_images
    print("✅ process_images 函数导入成功")
    
except ImportError as e:
    print(f"❌ 项目模块导入失败: {e}")
    print("🔧 尝试直接导入...")
    
    try:
        # 尝试直接从文件导入
        sys.path.insert(0, os.path.join(os.getcwd(), 'src', 'mcp_feedback_enhanced'))
        import server
        print("✅ 直接导入 server 模块成功")
        
        from server import process_images
        print("✅ process_images 函数导入成功")
        
    except ImportError as e2:
        print(f"❌ 直接导入也失败: {e2}")
        print("请检查项目结构")

# 测试图片序列化功能
print("\n🖼️ 测试图片序列化功能...")

try:
    # 创建测试图片数据
    import base64
    test_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU8ByQAAAABJRU5ErkJggg=="
    
    test_images = [{
        "name": "test.png",
        "data": base64.b64decode(test_png),
        "size": len(base64.b64decode(test_png))
    }]
    
    # 测试 process_images 函数
    if 'process_images' in locals():
        result = process_images(test_images)
        print(f"✅ process_images 测试成功，处理了 {len(result)} 张图片")
        
        # 测试序列化
        import json
        for i, img_content in enumerate(result):
            img_dict = {
                "type": img_content.type,
                "data": img_content.data[:50] + "...",  # 截断显示
                "mimeType": img_content.mimeType
            }
            json.dumps(img_dict)
        print("✅ 图片序列化测试通过")
    else:
        print("⚠️ process_images 函数未导入，跳过测试")
        
except Exception as e:
    print(f"❌ 图片序列化测试失败: {e}")

# 测试服务器启动能力
print("\n🚀 测试服务器启动能力...")

try:
    # 检查是否可以创建 FastMCP 实例
    mcp = FastMCP(name="TestServer")
    print("✅ FastMCP 实例创建成功")
    
    # 检查是否可以定义工具
    @mcp.tool()
    def test_tool() -> str:
        """测试工具"""
        return "测试成功"
    
    print("✅ 工具定义成功")
    
except Exception as e:
    print(f"❌ 服务器测试失败: {e}")

print("\n" + "=" * 40)
print("🎉 安装测试完成！")

# 检查关键文件
print("\n📁 检查项目文件...")
key_files = [
    "src/mcp_feedback_enhanced/__init__.py",
    "src/mcp_feedback_enhanced/__main__.py", 
    "src/mcp_feedback_enhanced/server.py",
    "pyproject.toml"
]

for file_path in key_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} 缺失")

print("\n🚀 启动建议:")
print("如果所有测试都通过，您可以运行:")
print("  PYTHONPATH=\"$PWD/src:$PYTHONPATH\" python3.11 -m mcp_feedback_enhanced")
print("\n或者使用调试模式:")
print("  MCP_DEBUG=true PYTHONPATH=\"$PWD/src:$PYTHONPATH\" python3.11 -m mcp_feedback_enhanced")
