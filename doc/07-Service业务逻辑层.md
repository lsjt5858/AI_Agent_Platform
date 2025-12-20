# 第07课：Service 业务逻辑层

## 🎯 本课目标

- 理解 Service 层的职责和设计
- 学习业务逻辑的组织方式
- 掌握服务间的协作模式

---

## 📖 什么是 Service 层？

Service（服务）层是**业务逻辑的核心**，位于 Router 和 Repository 之间。

### 职责对比

| 层级 | 职责 |
|------|------|
| **Router** | 接收请求、参数验证、返回响应 |
| **Service** | 业务逻辑、事务协调、服务编排 |
| **Repository** | 数据库 CRUD 操作 |

### 为什么需要 Service 层？

1. **业务逻辑复用** - 多个 Router 可以共用同一个 Service
2. **事务管理** - 在 Service 层统一管理事务
3. **服务编排** - 协调多个 Repository 完成复杂操作
4. **易于测试** - 业务逻辑独立于 HTTP 层

---

## 📝 AgentService 详解

查看 `app/services/agent.py`：

### 1. 服务类结构

```python
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.agent import Agent
from ..repositories.agent import AgentRepository
from ..schemas.agent import AgentCreate, AgentUpdate

class AgentNotFoundError(Exception):
    """Agent 未找到异常"""
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        super().__init__(f"Agent with id {agent_id} not found")

class AgentService:
    """Agent 业务逻辑服务"""

    def __init__(self, session: AsyncSession):
        self.repository = AgentRepository(session)
        self.session = session
```

**设计要点**：
- 自定义业务异常 `AgentNotFoundError`
- 在构造函数中创建 Repository 实例
- 保存 session 引用用于事务管理

### 2. 创建 Agent

```python
async def create_agent(self, data: AgentCreate) -> Agent:
    """创建新的 Agent"""
    agent = await self.repository.create(data)
    await self.session.commit()  # 提交事务
    return agent
```

**流程**：
1. 调用 Repository 创建 Agent
2. 提交事务
3. 返回创建的对象

### 3. 查询 Agent

```python
async def get_agents(self) -> List[Agent]:
    """获取所有 Agent"""
    return await self.repository.get_all()

async def get_agent(self, agent_id: int) -> Agent:
    """获取单个 Agent，不存在则抛异常"""
    agent = await self.repository.get_by_id(agent_id)
    if agent is None:
        raise AgentNotFoundError(agent_id)
    return agent
```

**业务规则**：
- 查询不存在的 Agent 时抛出业务异常
- 由 Router 层捕获并转换为 HTTP 404

### 4. 更新 Agent

```python
async def update_agent(self, agent_id: int, data: AgentUpdate) -> Agent:
    """更新 Agent"""
    agent = await self.repository.update(agent_id, data)
    if agent is None:
        raise AgentNotFoundError(agent_id)
    await self.session.commit()
    return agent
```

### 5. 删除 Agent

```python
async def delete_agent(self, agent_id: int) -> bool:
    """删除 Agent（级联删除关联对话）"""
    deleted = await self.repository.delete(agent_id)
    if not deleted:
        raise AgentNotFoundError(agent_id)
    await self.session.commit()
    return True
```

### 6. 工厂函数

```python
def get_agent_service(session: AsyncSession) -> AgentService:
    """创建 AgentService 实例的工厂函数"""
    return AgentService(session)
```

---

## 📊 MessageService - 复杂业务逻辑

`MessageService` 展示了更复杂的业务场景：

```python
class MessageService:
    """消息服务 - 整合 LLM 调用"""

    def __init__(
        self,
        session: AsyncSession,
        llm_service: LLMService | None = None
    ):
        self.message_repository = MessageRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.agent_repository = AgentRepository(session)
        self.llm_service = llm_service or get_llm_service()
        self.session = session
```

**特点**：
- 依赖多个 Repository
- 依赖外部服务（LLMService）

### 发送消息的业务流程

```python
async def send_message(
    self, 
    conversation_id: int, 
    content: str
) -> tuple[Message, Message]:
    """发送用户消息并获取 AI 回复"""
    
    # 1. 验证对话存在
    conversation = await self.conversation_repository.get_by_id(conversation_id)
    if conversation is None:
        raise ConversationNotFoundError(conversation_id)
    
    # 2. 获取 Agent 的系统提示
    agent = await self.agent_repository.get_by_id(conversation.agent_id)
    system_prompt = agent.system_prompt if agent else "You are helpful."
    
    # 3. 保存用户消息
    user_message = await self.message_repository.create(
        conversation_id=conversation_id,
        role="user",
        content=content
    )
    
    # 4. 构建上下文
    messages = await self.message_repository.get_by_conversation(conversation_id)
    message_context = self._build_message_context(messages)
    
    # 5. 调用 LLM 获取回复
    ai_response, token_usage = await self.llm_service.chat(
        messages=message_context,
        system_prompt=system_prompt
    )
    
    # 6. 保存 AI 回复
    assistant_message = await self.message_repository.create(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response
    )
    
    # 7. 提交事务
    await self.session.commit()
    
    return user_message, assistant_message
```

### 业务流程图

```
用户发送消息
      │
      ▼
┌─────────────────┐
│ 1. 验证对话存在  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 获取系统提示  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 保存用户消息  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 构建对话上下文│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. 调用 LLM API │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. 保存 AI 回复 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. 提交事务     │
└────────┬────────┘
         │
         ▼
返回两条消息
```

---

## 🔧 构建消息上下文

```python
def _build_message_context(self, messages: List[Message]) -> List[dict]:
    """将 Message 对象转换为 LLM 需要的格式"""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

**输入**（Message 对象列表）：
```python
[
    Message(role="user", content="你好"),
    Message(role="assistant", content="你好！有什么可以帮你?"),
    Message(role="user", content="今天天气怎么样?"),
]
```

**输出**（给 LLM 的格式）：
```python
[
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你?"},
    {"role": "user", "content": "今天天气怎么样?"},
]
```

---

## 📋 Service 设计原则

| 原则 | 说明 |
|------|------|
| 单一职责 | 每个 Service 负责一个业务领域 |
| 事务边界 | 在 Service 层管理事务 |
| 异常转换 | 将底层异常转为业务异常 |
| 依赖注入 | 通过构造函数注入依赖 |
| 无状态 | 不保存请求相关状态 |

---

## 🎓 动手练习

### 练习：添加对话标题自动生成

```python
async def create_conversation_with_title(
    self, 
    agent_id: int, 
    first_message: str
) -> Conversation:
    """创建对话并根据首条消息生成标题"""
    
    # 1. 创建对话
    conversation = await self.conversation_repository.create(agent_id)
    
    # 2. 使用 LLM 生成标题
    title = await self.llm_service.generate_title(first_message)
    
    # 3. 更新标题
    conversation.title = title
    
    await self.session.commit()
    return conversation
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 Service 层的职责 | ☐ |
| 会组织业务逻辑 | ☐ |
| 理解事务管理的位置 | ☐ |
| 会协调多个 Repository | ☐ |
| 会集成外部服务 | ☐ |

---

## 🔜 下一课预告

**第08课：依赖注入详解** - 深入学习 FastAPI 的依赖注入系统。
