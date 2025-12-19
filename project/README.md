# AI Agent Platform

一个前后端分离的 AI Agent 对话平台，使用 FastAPI 构建后端，集成大语言模型 API。

## 项目概述

这个项目帮助你学习和实践：
- **FastAPI** 后端开发（路由、依赖注入、Pydantic、异步编程）
- **前后端分离** 架构设计
- **大模型 API** 集成（通义千问/OpenAI）
- **SQLAlchemy** ORM 和异步数据库操作
- **RESTful API** 设计规范

## 核心功能

1. **Agent 管理** - 创建不同角色的 AI 智能体（代码助手、翻译助手等）
2. **多轮对话** - 与 Agent 进行上下文连贯的对话
3. **历史记录** - 保存和管理对话历史
4. **Web 界面** - 简洁的前端交互界面

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy (async)
- aiosqlite
- Pydantic
- httpx

### 前端
- HTML5 + CSS3
- Vanilla JavaScript
- Fetch API

### 数据库
- SQLite

## 项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/             # Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── repositories/        # 数据访问层
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── llm.py
│   └── routers/             # API 路由
│       ├── __init__.py
│       ├── agents.py
│       ├── conversations.py
│       └── messages.py
├── static/                  # 前端静态文件
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/                   # 测试文件
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── properties/
├── .env.example             # 环境变量模板
└── requirements.txt         # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
cd project
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 LLM API Key
```

### 3. 运行应用

```bash
uvicorn app.main:app --reload
```

### 4. 访问应用

- Web 界面: http://localhost:8000
- API 文档: http://localhost:8000/docs

## API 端点

### Agent 管理
- `POST /api/agents` - 创建 Agent
- `GET /api/agents` - 获取 Agent 列表
- `GET /api/agents/{id}` - 获取单个 Agent
- `PUT /api/agents/{id}` - 更新 Agent
- `DELETE /api/agents/{id}` - 删除 Agent

### 对话管理
- `POST /api/agents/{agent_id}/conversations` - 创建对话
- `GET /api/agents/{agent_id}/conversations` - 获取对话列表
- `GET /api/conversations/{id}` - 获取对话详情
- `DELETE /api/conversations/{id}` - 删除对话

### 消息
- `POST /api/conversations/{conversation_id}/messages` - 发送消息
- `GET /api/conversations/{conversation_id}/messages` - 获取消息历史

## 学习路径

建议按以下顺序实现：

1. **项目初始化** - 创建目录结构，配置依赖
2. **数据库模型** - 定义 Agent, Conversation, Message 模型
3. **Pydantic Schemas** - 定义请求/响应数据结构
4. **Repository 层** - 实现数据库 CRUD 操作
5. **LLM Service** - 集成大模型 API
6. **Service 层** - 实现业务逻辑
7. **API Router** - 实现 RESTful 端点
8. **前端界面** - 实现 Web 交互

## 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| LLM_API_KEY | 大模型 API Key | sk-xxx |
| LLM_API_BASE | API 基础 URL | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| LLM_MODEL | 模型名称 | qwen-turbo |
| DATABASE_URL | 数据库连接 | sqlite+aiosqlite:///./data.db |

## License

MIT
