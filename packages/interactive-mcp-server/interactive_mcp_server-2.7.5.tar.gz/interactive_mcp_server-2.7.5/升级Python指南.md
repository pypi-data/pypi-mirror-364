# 🐍 Python 升级指南

## 🚨 当前问题
您的 Python 版本是 3.9.6，但 MCP 需要 Python 3.10+

## 🔧 解决方案（按推荐程度排序）

### 方案一：使用 Homebrew 安装 Python 3.11（最简单）

```bash
# 1. 安装 Homebrew（如果没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装 Python 3.11
brew install python@3.11

# 3. 验证安装
python3.11 --version

# 4. 使用新的启动脚本
./智能启动.sh
```

### 方案二：使用 pyenv 管理多版本 Python（推荐）

```bash
# 1. 安装 pyenv
curl https://pyenv.run | bash

# 2. 添加到 shell 配置
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.zshrc

# 3. 重启终端或运行
source ~/.zshrc

# 4. 安装 Python 3.11
pyenv install 3.11.7

# 5. 在项目目录设置 Python 版本
cd /path/to/interactive-mcp-server
pyenv local 3.11.7

# 6. 验证版本
python --version

# 7. 运行启动脚本
./智能启动.sh
```

### 方案三：从官网下载安装包

1. **访问** https://www.python.org/downloads/
2. **下载** Python 3.11.x 的 macOS 安装包
3. **运行** 安装程序
4. **重启** 终端
5. **运行** `./智能启动.sh`

### 方案四：使用 conda（如果已安装）

```bash
# 创建新环境
conda create -n mcp-env python=3.11

# 激活环境
conda activate mcp-env

# 进入项目目录
cd /path/to/interactive-mcp-server

# 安装依赖
pip install -e .

# 启动服务器
python -m mcp_feedback_enhanced
```

## 🎯 推荐操作（最快方法）

### 如果您有 Homebrew：
```bash
brew install python@3.11
./智能启动.sh
```

### 如果您没有 Homebrew：
```bash
# 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.11

# 运行智能启动脚本
./智能启动.sh
```

## 🔍 检查当前系统

运行以下命令检查您的系统：

```bash
# 检查所有 Python 版本
ls /usr/bin/python* /usr/local/bin/python* /opt/homebrew/bin/python* 2>/dev/null

# 检查是否有 Homebrew
which brew

# 检查是否有 conda
which conda

# 检查是否有 pyenv
which pyenv
```

## ⚡ 快速验证

安装完成后，运行：

```bash
# 检查 Python 版本
python3.11 --version  # 应该显示 3.11.x

# 运行智能启动脚本
./智能启动.sh
```

## 🆘 如果遇到问题

### 问题1：command not found: brew
**解决：** 安装 Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 问题2：python3.11: command not found
**解决：** 检查安装路径并创建符号链接
```bash
# 查找 Python 3.11
find /usr -name "python3.11" 2>/dev/null
find /opt -name "python3.11" 2>/dev/null

# 如果找到，创建符号链接（例如）
sudo ln -sf /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11
```

### 问题3：权限错误
**解决：** 使用用户安装
```bash
pip install --user -e .
```

## 🎉 成功标志

当您看到以下输出时，表示成功：

```
✅ 使用 Python: python3.11 (版本 3.11.x)
✅ 依赖安装完成
✅ 所有模块导入成功
✅ 图片序列化测试通过
🎉 准备工作完成！
```

## 📞 需要帮助？

如果上述方法都不行，请：

1. **告诉我您的操作系统版本**：`sw_vers`
2. **告诉我是否有 Homebrew**：`which brew`
3. **告诉我当前的 Python 安装**：`which python3 && python3 --version`

我会为您提供更具体的解决方案！
