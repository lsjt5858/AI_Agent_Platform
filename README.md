# 🤖 AI Agent Platform

> 一个用于学习 FastAPI 和大语言模型 API 集成的实战项目

## 📚 项目简介

这是一个**学习型项目**，旨在帮助开发者通过实践掌握：

- 🚀 **FastAPI** 现代 Python Web 框架
- 🧠 **大语言模型 API** 集成（通义千问/OpenAI）
- 🏗️ **分层架构** 设计模式
- 🔄 **异步编程** 最佳实践
- 📊 **SQLAlchemy ORM** 数据库操作

## 🎯 学习目标

| 技术领域 | 学习内容 |
|---------|---------|
| FastAPI | 路由、依赖注入、中间件、异常处理、OpenAPI 文档 |
| 异步编程 | async/await、httpx、aiosqlite |
| 数据库 | SQLAlchemy ORM、异步会话、关系映射 |
| API 设计 | RESTful 规范、Pydantic 数据验证 |
| LLM 集成 | API 调用、消息格式化、上下文管理 |
| 测试 | pytest、异步测试、属性测试 |

## 🏛️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (静态页面)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Agent 列表   │  │   对话界面   │  │     Agent 创建表单       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP/REST (Fetch API)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     API Layer (Routers)                      │   │
│  │   /api/agents    │   /api/conversations   │   /api/messages  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Service Layer (业务逻辑)                   │   │
│  │   AgentService   │  ConversationService  │   LLMService      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Repository Layer (数据访问)                  │   │
│  │  AgentRepository │ ConversationRepository │ MessageRepository│   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────────────┐
│    SQLite Database   │              │      External LLM API        │
│  ┌────────────────┐  │              │  (通义千问 / OpenAI 兼容)     │
│  │     agents     │  │              │                              │
│  ├────────────────┤  │              │  POST /chat/completions      │
│  │ conversations  │  │              │                              │
│  ├────────────────┤  │              └──────────────────────────────┘
│  │    messages    │  │
│  └────────────────┘  │
└──────────────────────┘
```

## 📁 项目结构

```
AI_Agent_Platform/
├── README.md                    # 项目说明（本文件）
├── requirements.txt             # Python 依赖
└── project/                     # 主项目目录
    ├── app/                     # 应用代码
    │   ├── main.py             # FastAPI 入口，CORS、异常处理
    │   ├── config.py           # 配置管理 (pydantic-settings)
    │   ├── database.py         # 数据库连接和会话
    │   ├── models/             # SQLAlchemy ORM 模型
    │   │   ├── agent.py        # Agent 模型
    │   │   ├── conversation.py # Conversation 模型
    │   │   └── message.py      # Message 模型
    │   ├── schemas/            # Pydantic 数据验证
    │   │   ├── agent.py        # Agent 请求/响应 Schema
    │   │   ├── conversation.py # Conversation Schema
    │   │   ├── message.py      # Message Schema
    │   │   └── response.py     # 统一响应格式
    │   ├── repositories/       # 数据访问层 (DAL)
    │   │   ├── agent.py        # Agent CRUD
    │   │   ├── conversation.py # Conversation CRUD
    │   │   └── message.py      # Message CRUD
    │   ├── services/           # 业务逻辑层
    │   │   ├── agent.py        # Agent 业务逻辑
    │   │   ├── conversation.py # Conversation 业务逻辑
    │   │   ├── message.py      # 消息处理 + LLM 调用
    │   │   └── llm.py          # LLM API 封装
    │   └── routers/            # API 路由
    │       ├── agents.py       # /api/agents 端点
    │       ├── conversations.py# /api/conversations 端点
    │       └── messages.py     # /api/messages 端点
    ├── static/                 # 前端静态文件
    │   ├── index.html          # 主页面
    │   ├── style.css           # 样式
    │   └── app.js              # JavaScript 交互
    ├── tests/                  # 测试代码
    │   ├── conftest.py         # pytest 配置和 fixtures
    │   ├── unit/               # 单元测试
    │   ├── integration/        # 集成测试
    │   └── properties/         # 属性测试
    ├── .env.example            # 环境变量模板
    └── requirements.txt        # 项目依赖
```

## 🔄 数据流程

```
用户发送消息
      │
      ▼
┌─────────────────┐
│  MessageRouter  │  POST /api/conversations/{id}/messages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MessageService  │  1. 保存用户消息
│                 │  2. 构建上下文
│                 │  3. 调用 LLM
│                 │  4. 保存 AI 回复
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌───────┐
│  DB   │  │  LLM  │
│ 存储  │  │  API  │
└───────┘  └───────┘
```

## 🚀 快速开始

> 📖 **新手推荐**：查看 [保姆级启动指南](project/GETTING_STARTED.md)，包含详细的图文教程！

### 简要步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd AI_Agent_Platform

# 2. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
cd project
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key（参考下方说明）

# 5. 启动应用
uvicorn app.main:app --reload

# 6. 打开浏览器访问 http://localhost:8000
```

### 获取 LLM API Key

| 平台 | 获取地址 | 推荐 |
|------|---------|------|
| 通义千问 | [阿里云百炼](https://bailian.console.aliyun.com/) | ⭐ 国内推荐 |
| OpenAI | [OpenAI Platform](https://platform.openai.com/) | 需要科学上网 |
| DeepSeek | [DeepSeek](https://platform.deepseek.com/) | 性价比高 |

### 访问应用

| 地址 | 说明 |
|------|------|
| http://localhost:8000 | Web 界面 |
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/redoc | ReDoc API 文档 |

## 📡 API 端点

### Agent 管理

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/agents` | 创建 Agent |
| GET | `/api/agents` | 获取所有 Agent |
| GET | `/api/agents/{id}` | 获取单个 Agent |
| PUT | `/api/agents/{id}` | 更新 Agent |
| DELETE | `/api/agents/{id}` | 删除 Agent |

### 对话管理

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/agents/{agent_id}/conversations` | 创建对话 |
| GET | `/api/agents/{agent_id}/conversations` | 获取对话列表 |
| GET | `/api/conversations/{id}` | 获取对话详情 |
| DELETE | `/api/conversations/{id}` | 删除对话 |

### 消息

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/conversations/{id}/messages` | 发送消息并获取 AI 回复 |
| GET | `/api/conversations/{id}/messages` | 获取消息历史 |

## ⚙️ 环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `LLM_API_KEY` | 大模型 API Key | `sk-xxx` |
| `LLM_API_BASE_URL` | API 基础 URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `LLM_MODEL` | 模型名称 | `qwen-turbo` |
| `LLM_TIMEOUT` | 请求超时(秒) | `30` |
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./data.db` |

## 🧪 运行测试

```bash
cd project
python -m pytest -v
```

## 📖 学习路径建议

1. **阅读代码** - 从 `main.py` 开始，理解 FastAPI 应用结构
2. **理解分层** - 学习 Router → Service → Repository 的调用链
3. **数据库操作** - 研究 SQLAlchemy 异步 ORM 的使用
4. **LLM 集成** - 查看 `services/llm.py` 了解 API 调用方式
5. **动手实践** - 尝试添加新功能或修改现有功能

## 🎓 适合人群

- 想学习 FastAPI 的 Python 开发者
- 对大语言模型 API 集成感兴趣的开发者
- 希望了解分层架构设计的初学者
- 想实践异步编程的开发者

## 📄 License

MIT

---

> 💡 **提示**: 这是一个学习项目，代码结构清晰，注释详细，非常适合作为 FastAPI 和 LLM 集成的入门参考。
