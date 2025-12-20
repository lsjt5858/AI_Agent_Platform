# 第02课：FastAPI 入门

## 🎯 本课目标

- 理解 FastAPI 的核心概念
- 学习创建路由和处理请求
- 掌握路径参数和查询参数的使用

---

## 📖 什么是 FastAPI？

FastAPI 是一个现代、高性能的 Python Web 框架，主要特点：

| 特点 | 说明 |
|------|------|
| 🚀 高性能 | 基于 Starlette 和 Pydantic，性能媲美 Go/Node.js |
| 📝 自动文档 | 自动生成 OpenAPI (Swagger) 文档 |
| ✅ 类型提示 | 基于 Python 类型注解，编辑器支持更好 |
| 🔄 异步支持 | 原生支持 async/await |

---

## 🔍 解析项目入口文件

让我们分析 `app/main.py`：

### 2.1 基础导入

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
```

| 导入项 | 用途 |
|--------|------|
| `FastAPI` | 核心应用类 |
| `Request` | HTTP 请求对象 |
| `CORSMiddleware` | 跨域资源共享中间件 |
| `JSONResponse` | JSON 格式响应 |
| `FileResponse` | 文件响应 |

### 2.2 创建应用实例

```python
app = FastAPI(
    title="AI Agent Platform",
    description="AI Agent 对话平台 - 创建和管理多个 AI 智能体",
    version="1.0.0",
    docs_url="/docs",      # Swagger 文档地址
    redoc_url="/redoc",    # ReDoc 文档地址
)
```

**参数说明**：

| 参数 | 作用 | 示例值 |
|------|------|--------|
| `title` | API 文档标题 | "AI Agent Platform" |
| `description` | API 描述 | 项目简介 |
| `version` | API 版本 | "1.0.0" |
| `docs_url` | Swagger UI 路径 | "/docs" |
| `redoc_url` | ReDoc 路径 | "/redoc" |

### 2.3 配置 CORS 中间件

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # 允许的源
    allow_credentials=True,        # 允许携带凭证
    allow_methods=["*"],           # 允许的 HTTP 方法
    allow_headers=["*"],           # 允许的请求头
)
```

> 💡 **什么是 CORS？**  
> 跨域资源共享（Cross-Origin Resource Sharing）。当前端和后端不在同一个域时，浏览器会阻止请求。配置 CORS 中间件允许跨域访问。

---

## 📝 路由基础

### 3.1 简单路由

```python
@app.get("/")
async def root():
    """根路径 - 返回欢迎信息"""
    return {"message": "欢迎使用 AI Agent 对话平台"}
```

**解析**：

| 元素 | 说明 |
|------|------|
| `@app.get("/")` | 装饰器，定义 GET 请求处理器 |
| `async def` | 定义异步函数 |
| `return {...}` | FastAPI 自动转换为 JSON 响应 |

### 3.2 健康检查接口

```python
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "success": True,
        "data": {"status": "healthy"},
        "error": None,
    }
```

> 💡 **为什么需要健康检查？**  
> 用于监控系统判断服务是否正常运行，在容器化部署中尤为重要。

---

## 🔧 路由注册

### 4.1 使用 APIRouter

项目使用模块化的路由设计：

```python
from .routers import agents_router, conversations_router, messages_router

# 注册路由，添加 /api 前缀
app.include_router(agents_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
```

**效果**：

| 模块 | 实际路径示例 |
|------|-------------|
| agents_router | `/api/agents`, `/api/agents/{id}` |
| conversations_router | `/api/conversations/{id}` |
| messages_router | `/api/conversations/{id}/messages` |

### 4.2 查看 routers/__init__.py

```python
from .agents import router as agents_router
from .conversations import router as conversations_router
from .messages import router as messages_router

__all__ = ["agents_router", "conversations_router", "messages_router"]
```

---

## 🎓 动手练习

### 练习 1：添加一个新路由

在 `main.py` 中添加：

```python
@app.get("/api/info")
async def api_info():
    """返回 API 信息"""
    return {
        "success": True,
        "data": {
            "name": "AI Agent Platform API",
            "version": "1.0.0",
            "author": "你的名字"
        },
        "error": None
    }
```

**验证**：访问 `http://localhost:8000/api/info`

### 练习 2：添加路径参数

```python
@app.get("/api/hello/{name}")
async def say_hello(name: str):
    """向指定用户问好"""
    return {
        "success": True,
        "data": {"message": f"你好，{name}！"},
        "error": None
    }
```

**验证**：访问 `http://localhost:8000/api/hello/小明`

---

## 📊 HTTP 方法对照

| HTTP 方法 | FastAPI 装饰器 | 常见用途 |
|-----------|---------------|---------|
| GET | `@app.get()` | 获取数据 |
| POST | `@app.post()` | 创建数据 |
| PUT | `@app.put()` | 更新数据（全量）|
| PATCH | `@app.patch()` | 更新数据（部分）|
| DELETE | `@app.delete()` | 删除数据 |

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 FastAPI 特点和优势 | ☐ |
| 会创建 FastAPI 应用实例 | ☐ |
| 理解 CORS 的作用 | ☐ |
| 会定义简单路由 | ☐ |
| 理解模块化路由设计 | ☐ |
| 会使用路径参数 | ☐ |

---

## 🔜 下一课预告

**第03课：Pydantic 数据验证** - 学习如何使用 Pydantic 进行请求/响应数据验证。
