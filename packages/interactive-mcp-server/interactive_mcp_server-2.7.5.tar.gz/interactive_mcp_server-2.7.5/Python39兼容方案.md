# Python 3.9 兼容解决方案

## 🚨 问题分析

您的系统使用 Python 3.9.6，但是：
- **FastMCP** 需要 Python 3.10+
- **MCP** 需要 Python 3.10+

## 🔧 解决方案

### 方案一：升级 Python（推荐）

#### macOS 用户：
```bash
# 使用 Homebrew 安装 Python 3.11
brew install python@3.11

# 验证安装
python3.11 --version

# 使用新版本 Python
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

#### 使用 pyenv（推荐）：
```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 重启终端或运行
source ~/.bashrc

# 安装 Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7

# 验证版本
python --version

# 重新运行安装
./快速启动.sh
```

### 方案二：创建兼容版本（临时方案）

我将为您创建一个简化版本，不依赖 FastMCP：

```bash
# 创建简化版服务器
python3 -c "
import sys
print(f'当前 Python 版本: {sys.version}')
print('创建兼容版本...')
"
```

### 方案三：使用 Docker（隔离环境）

```bash
# 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8000
CMD ["python", "-m", "mcp_feedback_enhanced"]
EOF

# 构建和运行
docker build -t mcp-feedback .
docker run -p 8000:8000 mcp-feedback
```

## 🎯 推荐操作步骤

### 1. 检查是否有其他 Python 版本
```bash
# 检查系统中的 Python 版本
ls /usr/bin/python*
ls /usr/local/bin/python*

# 检查是否有 python3.10 或更高版本
python3.10 --version 2>/dev/null || echo "Python 3.10 未安装"
python3.11 --version 2>/dev/null || echo "Python 3.11 未安装"
python3.12 --version 2>/dev/null || echo "Python 3.12 未安装"
```

### 2. 如果找到了更高版本的 Python
```bash
# 使用找到的版本（例如 python3.11）
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
python3.11 -m mcp_feedback_enhanced
```

### 3. 如果没有更高版本，安装 Python 3.11

#### macOS (使用 Homebrew):
```bash
# 安装 Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3.11
brew install python@3.11

# 创建符号链接
ln -sf /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11
```

#### macOS (官方安装包):
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11.x 安装包
3. 运行安装程序
4. 重新运行我们的脚本

## 🔄 更新后的启动脚本

我将创建一个支持多版本 Python 的启动脚本：
