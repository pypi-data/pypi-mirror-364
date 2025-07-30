#!/usr/bin/env python3
"""
简单的 MCP 测试客户端
用于测试 MCP Feedback Enhanced 服务器
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_server():
    """测试 MCP 服务器"""
    print("🧪 MCP 服务器测试客户端")
    print("=" * 40)
    
    # 服务器启动命令
    server_cmd = [
        "python3.11", 
        "-m", 
        "mcp_feedback_enhanced"
    ]
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}/src:{env.get('PYTHONPATH', '')}"
    env["MCP_DEBUG"] = "true"
    
    print(f"🚀 启动服务器: {' '.join(server_cmd)}")
    print(f"📁 工作目录: {os.getcwd()}")
    
    try:
        # 启动服务器进程
        process = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=os.getcwd()
        )
        
        print("✅ 服务器进程已启动")
        
        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 收到响应: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        
        # 发送 initialized 通知
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # 列出可用工具
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        print("📤 请求工具列表...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # 读取工具列表响应
        tools_response_line = process.stdout.readline()
        if tools_response_line:
            tools_response = json.loads(tools_response_line.strip())
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"🛠️ 可用工具数量: {len(tools)}")
            for tool in tools:
                print(f"   - {tool.get('name')}: {tool.get('description', 'No description')}")
        
        # 测试 interactive_feedback 工具
        if tools:
            print("\n🧪 测试 interactive_feedback 工具...")
            
            call_tool_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "interactive_feedback",
                    "arguments": {
                        "project_directory": os.getcwd(),
                        "summary": "测试图片序列化修复",
                        "timeout": 10  # 短超时用于测试
                    }
                }
            }
            
            print("📤 调用 interactive_feedback 工具...")
            process.stdin.write(json.dumps(call_tool_request) + "\n")
            process.stdin.flush()
            
            # 等待响应（可能需要一些时间）
            print("⏳ 等待响应（Web UI 应该会打开）...")
            
            # 读取响应
            import select
            import time
            
            start_time = time.time()
            while time.time() - start_time < 15:  # 等待最多15秒
                if select.select([process.stdout], [], [], 1)[0]:
                    response_line = process.stdout.readline()
                    if response_line:
                        try:
                            response = json.loads(response_line.strip())
                            if response.get('id') == 3:
                                result = response.get('result', {})
                                content = result.get('content', [])
                                print(f"✅ 工具调用成功，返回 {len(content)} 个内容项")
                                
                                for i, item in enumerate(content):
                                    if item.get('type') == 'text':
                                        text = item.get('text', '')[:100]
                                        print(f"   文本 {i+1}: {text}...")
                                    elif item.get('type') == 'image':
                                        print(f"   图片 {i+1}: {item.get('mimeType', 'unknown')}")
                                break
                        except json.JSONDecodeError:
                            continue
                else:
                    print(".", end="", flush=True)
            
            print("\n")
        
        # 清理
        print("🧹 清理进程...")
        process.terminate()
        process.wait(timeout=5)
        
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        if 'process' in locals():
            process.terminate()

def main():
    """主函数"""
    print("🔧 MCP Feedback Enhanced 测试客户端")
    print("这个客户端会测试您的 MCP 服务器是否正常工作")
    print()
    
    # 检查是否在正确目录
    if not os.path.exists("pyproject.toml"):
        print("❌ 请在项目根目录运行此脚本")
        print(f"当前目录: {os.getcwd()}")
        return 1
    
    # 检查 Python 版本
    if not os.path.exists("venv_py311"):
        print("❌ 请先运行 ./智能启动.sh 设置环境")
        return 1
    
    # 运行测试
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
