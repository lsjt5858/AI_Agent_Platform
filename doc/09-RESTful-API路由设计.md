# 第09课：RESTful API 路由设计

## 🎯 本课目标

- 理解 RESTful API 设计原则
- 学习 FastAPI 路由器的使用
- 掌握完整的 CRUD API 实现

---

## 📖 什么是 RESTful API？

REST（Representational State Transfer）是一种 API 设计风格。

### 核心原则

| 原则 | 说明 |
|------|------|
| 资源导向 | URL 表示资源，如 `/agents`、`/messages` |
| HTTP 方法 | 用 GET/POST/PUT/DELETE 表示操作 |
| 无状态 | 每个请求包含所需的全部信息 |
| 统一接口 | 使用标准 HTTP 方法和状态码 |

### HTTP 方法与 CRUD

| HTTP 方法 | 操作 | 示例 |
|-----------|------|------|
| GET | 读取 | 获取 Agent 列表 |
| POST | 创建 | 创建新 Agent |
| PUT | 更新 | 更新 Agent 信息 |
| DELETE | 删除 | 删除 Agent |

---

## 🔍 项目 API 结构

```
/api
├── /agents                      # Agent 资源
│   ├── GET    /                # 获取所有
│   ├── POST   /                # 创建
│   ├── GET    /{id}            # 获取单个
│   ├── PUT    /{id}            # 更新
│   └── DELETE /{id}            # 删除
│
├── /agents/{id}/conversations   # 嵌套资源
│   ├── GET    /                # 获取对话列表
│   └── POST   /                # 创建对话
│
├── /conversations              # Conversation 资源
│   ├── GET    /{id}           # 获取对话详情
│   └── DELETE /{id}           # 删除对话
│
└── /conversations/{id}/messages # 嵌套资源
    ├── GET    /                # 获取消息列表
    └── POST   /                # 发送消息
```

---

## 📝 Agent Router 详解

查看 `app/routers/agents.py`：

### 1. 创建路由器

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(
    prefix="/agents",           # URL 前缀
    tags=["智能体管理"]          # API 文档分组
)
```

### 2. POST - 创建资源

```python
@router.post(
    "",                                        # 路径（完整: /api/agents）
    response_model=APIResponse[AgentResponse], # 响应模型
    status_code=status.HTTP_201_CREATED,       # 创建成功返回 201
    summary="创建新的智能体",                   # 简短描述
    description="创建新的 AI 智能体"            # 详细描述
)
async def create_agent(
    data: AgentCreate,                         # 请求体（自动验证）
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    """
    创建新的智能体。

    - **name**: 智能体名称（必填）
    - **system_prompt**: 系统提示
    - **description**: 描述（可选）
    """
    agent = await service.create_agent(data)
    return APIResponse.ok(AgentResponse.model_validate(agent))
```

**要点**：
- `status.HTTP_201_CREATED` - 创建资源返回 201
- `AgentCreate` 作为请求体参数自动验证
- 文档字符串用于 API 文档

### 3. GET - 获取列表

```python
@router.get(
    "",
    response_model=APIResponse[List[AgentResponse]],
    summary="获取所有智能体"
)
async def get_agents(
    service: AgentService = Depends(get_service)
) -> APIResponse[List[AgentResponse]]:
    """获取所有智能体列表"""
    agents = await service.get_agents()
    return APIResponse.ok([AgentResponse.model_validate(a) for a in agents])
```

### 4. GET - 获取单个

```python
@router.get(
    "/{agent_id}",                    # 路径参数
    response_model=APIResponse[AgentResponse],
    summary="根据ID获取智能体"
)
async def get_agent(
    agent_id: int,                    # 从路径提取
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    try:
        agent = await service.get_agent(agent_id)
        return APIResponse.ok(AgentResponse.model_validate(agent))
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Agent with id {agent_id} not found"
                }
            }
        )
```

**要点**：
- `{agent_id}` 路径参数
- 捕获业务异常，转换为 HTTP 404

### 5. PUT - 更新资源

```python
@router.put(
    "/{agent_id}",
    response_model=APIResponse[AgentResponse],
    summary="更新智能体"
)
async def update_agent(
    agent_id: int,
    data: AgentUpdate,
    service: AgentService = Depends(get_service)
) -> APIResponse[AgentResponse]:
    try:
        agent = await service.update_agent(agent_id, data)
        return APIResponse.ok(AgentResponse.model_validate(agent))
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Agent not found"}
        )
```

### 6. DELETE - 删除资源

```python
@router.delete(
    "/{agent_id}",
    response_model=APIResponse[dict],
    summary="删除智能体"
)
async def delete_agent(
    agent_id: int,
    service: AgentService = Depends(get_service)
) -> APIResponse[dict]:
    try:
        await service.delete_agent(agent_id)
        return APIResponse.ok({"deleted": True, "agent_id": agent_id})
    except AgentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Agent not found"}
        )
```

---

## 📊 嵌套资源设计

对于有层级关系的资源，使用嵌套路由：

```python
# 对话属于某个 Agent
# /api/agents/{agent_id}/conversations

@router.post("/agents/{agent_id}/conversations")
async def create_conversation(
    agent_id: int,
    data: ConversationCreate = None,
    service: ConversationService = Depends(get_service)
):
    conversation = await service.create_conversation(agent_id, data)
    return APIResponse.ok(ConversationDetail.model_validate(conversation))
```

```python
# 消息属于某个对话
# /api/conversations/{conversation_id}/messages

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    data: MessageCreate,
    service: MessageService = Depends(get_service)
):
    user_msg, ai_msg = await service.send_message(
        conversation_id, 
        data.content
    )
    return APIResponse.ok({
        "user_message": MessageResponse.model_validate(user_msg),
        "assistant_message": MessageResponse.model_validate(ai_msg)
    })
```

---

## 🔧 注册路由到应用

```python
# app/main.py

from .routers import agents_router, conversations_router, messages_router

# 注册路由，统一添加 /api 前缀
app.include_router(agents_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
```

**最终 URL 结构**：
```
/api/agents              ← agents_router
/api/conversations       ← conversations_router
/api/conversations/*/messages  ← messages_router
```

---

## 📋 HTTP 状态码规范

| 状态码 | 场景 |
|--------|------|
| 200 OK | GET/PUT/DELETE 成功 |
| 201 Created | POST 创建成功 |
| 400 Bad Request | 请求参数错误 |
| 404 Not Found | 资源不存在 |
| 422 Unprocessable Entity | 验证失败 |
| 500 Internal Server Error | 服务器错误 |

---

## 🎓 动手练习

### 练习：添加分页参数

```python
@router.get("/agents")
async def get_agents(
    skip: int = 0,                # 查询参数
    limit: int = 100,             # 查询参数
    service: AgentService = Depends(get_service)
):
    """
    获取智能体列表（支持分页）
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    """
    agents = await service.get_agents(skip=skip, limit=limit)
    return APIResponse.ok([AgentResponse.model_validate(a) for a in agents])
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 RESTful 设计原则 | ☐ |
| 会使用 APIRouter | ☐ |
| 会实现 CRUD 路由 | ☐ |
| 理解路径参数和请求体 | ☐ |
| 理解嵌套资源设计 | ☐ |
| 掌握 HTTP 状态码使用 | ☐ |

---

## 🔜 下一课预告

**第10课：异常处理与错误响应** - 学习全局异常处理和错误响应设计。
