# 🚀 AI Agent Platform 保姆级启动指南

> 本文档将手把手教你如何从零开始运行这个项目，即使你是新手也能轻松上手！

## 📋 目录

1. [环境要求](#-环境要求)
2. [第一步：安装 Python](#-第一步安装-python)
3. [第二步：下载项目](#-第二步下载项目)
4. [第三步：创建虚拟环境](#-第三步创建虚拟环境)
5. [第四步：安装依赖](#-第四步安装依赖)
6. [第五步：配置环境变量](#-第五步配置环境变量)
7. [第六步：获取 LLM API Key](#-第六步获取-llm-api-key)
8. [第七步：启动项目](#-第七步启动项目)
9. [第八步：使用项目](#-第八步使用项目)
10. [常见问题](#-常见问题)

---

## 📦 环境要求

在开始之前，请确保你的电脑满足以下要求：

| 要求 | 说明 |
|------|------|
| 操作系统 | Windows 10+、macOS 10.15+、Linux |
| Python | 3.10 或更高版本 |
| 网络 | 能够访问互联网（调用 LLM API） |
| 磁盘空间 | 至少 500MB 可用空间 |

---

## 🐍 第一步：安装 Python

### 检查是否已安装 Python

打开终端（Terminal）或命令提示符（CMD），输入：

```bash
python --version
```

或者（macOS/Linux）：

```bash
python3 --version
```

如果显示 `Python 3.10.x` 或更高版本，说明已安装，可以跳到[第二步](#-第二步下载项目)。

### 安装 Python（如果未安装）

#### Windows 用户

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 点击 "Download Python 3.x.x" 下载安装包
3. 运行安装程序
4. ⚠️ **重要**：勾选 "Add Python to PATH" 选项！
5. 点击 "Install Now"
6. 安装完成后，重新打开命令提示符验证

#### macOS 用户

**方法一：使用 Homebrew（推荐）**

```bash
# 如果没有 Homebrew，先安装它
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python
brew install python@3.11
```

**方法二：官网下载**

1. 访问 [Python 官网](https://www.python.org/downloads/macos/)
2. 下载 macOS 安装包
3. 双击安装

#### Linux 用户（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

---

## 📥 第二步：下载项目

### 方法一：使用 Git（推荐）

```bash
# 克隆项目
git clone <你的仓库地址>

# 进入项目目录
cd AI_Agent_Platform
```

### 方法二：直接下载 ZIP

1. 在 GitHub 页面点击绿色的 "Code" 按钮
2. 选择 "Download ZIP"
3. 解压到你想要的位置
4. 打开终端，进入解压后的目录

---

## 🔧 第三步：创建虚拟环境

虚拟环境可以隔离项目依赖，避免与其他项目冲突。

### Windows 用户

```bash
# 进入项目目录
cd AI_Agent_Platform

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

激活成功后，命令行前面会出现 `(venv)` 标识：

```
(venv) C:\Users\你的用户名\AI_Agent_Platform>
```

### macOS / Linux 用户

```bash
# 进入项目目录
cd AI_Agent_Platform

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

激活成功后，命令行前面会出现 `(venv)` 标识：

```
(venv) ~/AI_Agent_Platform$
```

### 💡 小贴士

- 每次打开新的终端窗口，都需要重新激活虚拟环境
- 退出虚拟环境：输入 `deactivate`

---

## 📚 第四步：安装依赖

确保虚拟环境已激活（命令行前有 `(venv)`），然后执行：

```bash
# 进入 project 目录
cd project

# 安装所有依赖
pip install -r requirements.txt
```

### 安装过程说明

这个命令会安装以下依赖包：

| 包名 | 用途 |
|------|------|
| fastapi | Web 框架 |
| uvicorn | ASGI 服务器 |
| sqlalchemy | 数据库 ORM |
| aiosqlite | SQLite 异步驱动 |
| httpx | HTTP 客户端（调用 LLM API） |
| pydantic | 数据验证 |
| pytest | 测试框架 |

安装可能需要 1-3 分钟，请耐心等待。

### 验证安装

```bash
pip list
```

如果看到 `fastapi`、`uvicorn` 等包，说明安装成功。

---

## ⚙️ 第五步：配置环境变量

### 5.1 复制配置文件

```bash
# 确保在 project 目录下
cp .env.example .env
```

Windows 用户如果 `cp` 命令不可用，可以使用：

```bash
copy .env.example .env
```

### 5.2 编辑配置文件

使用任意文本编辑器打开 `project/.env` 文件：

```bash
# macOS
open .env

# Windows
notepad .env

# Linux
nano .env
# 或
vim .env
```

### 5.3 配置文件说明

```bash
# ============ 应用设置 ============
APP_NAME=AI Agent Platform    # 应用名称，可以不改
DEBUG=true                    # 调试模式，开发时保持 true

# ============ 数据库配置 ============
DATABASE_URL=sqlite+aiosqlite:///./ai_agent.db
# 使用 SQLite 数据库，数据会保存在 ai_agent.db 文件中
# 一般不需要修改

# ============ LLM API 配置（重要！）============
# 通义千问配置（推荐国内用户使用）
LLM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=你的API密钥        # ⚠️ 必须修改！
LLM_MODEL=qwen-turbo          # 模型名称
LLM_TIMEOUT=30                # 超时时间（秒）

# OpenAI 配置（可选，需要能访问 OpenAI）
# LLM_API_BASE_URL=https://api.openai.com/v1
# LLM_API_KEY=sk-your-openai-key
# LLM_MODEL=gpt-3.5-turbo

# ============ CORS 设置 ============
# 跨域配置，一般不需要修改
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

---

## 🔑 第六步：获取 LLM API Key

你需要一个大语言模型的 API Key 才能让 AI 回复消息。以下是获取方式：

### 方案一：通义千问（推荐国内用户）

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 使用支付宝或阿里云账号登录
3. 进入控制台后，点击左侧菜单 "API-KEY 管理"
4. 点击 "创建 API-KEY"
5. 复制生成的 API Key

**配置示例：**

```bash
LLM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=qwen-turbo
```

**可用模型：**

| 模型名称 | 说明 |
|---------|------|
| qwen-turbo | 速度快，适合日常对话 |
| qwen-plus | 效果更好，稍慢 |
| qwen-max | 最强模型，较慢 |

### 方案二：OpenAI

1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key

**配置示例：**

```bash
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=gpt-3.5-turbo
```

### 方案三：其他兼容 OpenAI 格式的服务

如 DeepSeek、智谱 AI 等，只需修改 `LLM_API_BASE_URL` 和 `LLM_API_KEY`。

---

## 🎬 第七步：启动项目

### 7.1 确认当前位置

```bash
# 确保在 project 目录下
pwd
# 应该显示类似：/xxx/AI_Agent_Platform/project
```

### 7.2 启动服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `app.main:app` | 指定 FastAPI 应用位置 |
| `--reload` | 代码修改后自动重启（开发模式） |
| `--host 0.0.0.0` | 允许外部访问 |
| `--port 8000` | 端口号 |

### 7.3 启动成功标志

如果看到以下输出，说明启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 7.4 停止服务器

按 `Ctrl + C` 停止服务器。

---

## 🎮 第八步：使用项目

### 8.1 访问 Web 界面

打开浏览器，访问：

```
http://localhost:8000
```

你将看到 AI Agent 平台的主界面。

### 8.2 访问 API 文档

FastAPI 自动生成交互式 API 文档：

| 地址 | 说明 |
|------|------|
| http://localhost:8000/docs | Swagger UI（推荐） |
| http://localhost:8000/redoc | ReDoc 文档 |

### 8.3 基本使用流程

#### 1️⃣ 创建 Agent

1. 在 Web 界面点击 "创建 Agent"
2. 输入名称，如 "代码助手"
3. 输入系统提示词，如 "你是一个专业的 Python 编程助手"
4. 点击创建

#### 2️⃣ 开始对话

1. 点击刚创建的 Agent
2. 在输入框输入消息
3. 点击发送，等待 AI 回复

#### 3️⃣ 使用 API（可选）

使用 curl 测试 API：

```bash
# 创建 Agent
curl -X POST "http://localhost:8000/api/agents" \
  -H "Content-Type: application/json" \
  -d '{"name": "测试助手", "system_prompt": "你是一个友好的助手"}'

# 获取所有 Agent
curl "http://localhost:8000/api/agents"
```

---

## ❓ 常见问题

### Q1: 提示 "python 不是内部或外部命令"

**原因**：Python 没有添加到系统 PATH

**解决**：
1. 重新安装 Python，勾选 "Add Python to PATH"
2. 或手动添加 Python 到环境变量

### Q2: pip install 报错 "Could not find a version"

**原因**：pip 版本过旧或网络问题

**解决**：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 启动时报错 "Address already in use"

**原因**：8000 端口被占用

**解决**：

```bash
# 使用其他端口
uvicorn app.main:app --reload --port 8001
```

### Q4: LLM API 调用失败

**可能原因**：
1. API Key 错误或过期
2. 网络无法访问 API 服务
3. 账户余额不足

**解决**：
1. 检查 `.env` 文件中的 `LLM_API_KEY` 是否正确
2. 确认网络可以访问 API 地址
3. 登录对应平台检查账户状态

### Q5: 数据库错误 "no such table"

**原因**：数据库表未创建

**解决**：删除 `ai_agent.db` 文件，重启应用会自动创建。

### Q6: 虚拟环境激活失败（Windows）

**原因**：PowerShell 执行策略限制

**解决**：

```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q7: macOS 提示 "command not found: python"

**解决**：使用 `python3` 代替 `python`

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 🔄 日常使用流程

每次使用项目时，按以下步骤操作：

```bash
# 1. 打开终端，进入项目目录
cd AI_Agent_Platform

# 2. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 3. 进入 project 目录
cd project

# 4. 启动服务器
uvicorn app.main:app --reload

# 5. 打开浏览器访问 http://localhost:8000
```

---

## 🧪 运行测试

```bash
# 确保在 project 目录下，虚拟环境已激活
python -m pytest -v
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看本文档的 [常见问题](#-常见问题) 部分
2. 查看项目的 Issues 页面
3. 提交新的 Issue 描述你的问题

---

> 🎉 恭喜你完成了项目的启动！现在可以开始探索和学习了！
