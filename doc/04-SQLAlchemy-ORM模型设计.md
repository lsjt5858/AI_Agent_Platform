# 第04课：SQLAlchemy ORM 模型设计

## 🎯 本课目标

- 理解 ORM 的概念和优势
- 学习 SQLAlchemy 2.0 声明式语法
- 掌握模型关系（一对多）的定义

---

## 📖 什么是 ORM？

ORM（Object-Relational Mapping）是一种将数据库表映射为 Python 对象的技术。

### 对比：原生 SQL vs ORM

**原生 SQL**：
```python
cursor.execute(
    "INSERT INTO agents (name, system_prompt) VALUES (?, ?)",
    ("小助手", "You are helpful")
)
```

**ORM 方式**：
```python
agent = Agent(name="小助手", system_prompt="You are helpful")
session.add(agent)
await session.commit()
```

### ORM 优势

| 优势 | 说明 |
|------|------|
| 面向对象 | 用类和对象操作数据库 |
| 自动 SQL | 自动生成 SQL 语句 |
| 防注入 | 自动处理参数，防止 SQL 注入 |
| 跨数据库 | 支持多种数据库（SQLite、MySQL、PostgreSQL）|

---

## 🏗️ 项目数据模型

本项目包含三个核心模型：

```
┌─────────────────────────────────────────────────────┐
│                      Agent                          │
│  (智能体)                                            │
│  - id, name, system_prompt, description             │
│  - created_at, updated_at                           │
└──────────────────────┬──────────────────────────────┘
                       │ 1
                       │
                       │ *（一对多）
                       ▼
┌─────────────────────────────────────────────────────┐
│                   Conversation                       │
│  (对话)                                              │
│  - id, agent_id, title                              │
│  - created_at, updated_at                           │
└──────────────────────┬──────────────────────────────┘
                       │ 1
                       │
                       │ *（一对多）
                       ▼
┌─────────────────────────────────────────────────────┐
│                     Message                          │
│  (消息)                                              │
│  - id, conversation_id, role, content               │
│  - created_at                                       │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Agent 模型详解

查看 `app/models/agent.py`：

```python
from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

class Agent(Base):
    """AI 智能体模型"""
    
    __tablename__ = "agents"  # 表名

    # 主键
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 普通字段
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(
        Text, 
        nullable=False, 
        default="You are a helpful assistant."
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # 时间戳字段
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )

    # 关系：一个 Agent 有多个 Conversation
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="agent",
        cascade="all, delete-orphan"
    )
```

### 关键概念解析

#### 1. 表名定义
```python
__tablename__ = "agents"
```

#### 2. 字段映射
```python
# Mapped[类型] 声明字段类型
# mapped_column() 定义列属性
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
name: Mapped[str] = mapped_column(String(100), nullable=False)
```

| 参数 | 作用 |
|------|------|
| `primary_key=True` | 设为主键 |
| `autoincrement=True` | 自动递增 |
| `nullable=False` | 不允许为空 |
| `default=xxx` | Python 层默认值 |
| `server_default=xxx` | 数据库层默认值 |

#### 3. 时间戳自动管理
```python
created_at: Mapped[datetime] = mapped_column(
    DateTime,
    server_default=func.now()      # 创建时自动设置
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    server_default=func.now(),
    onupdate=func.now()            # 更新时自动更新
)
```

---

## 🔗 模型关系定义

### 一对多关系

**Agent → Conversation（一对多）**

在 Agent 模型中：
```python
# 一个 Agent 有多个 Conversation
conversations: Mapped[List["Conversation"]] = relationship(
    "Conversation",
    back_populates="agent",
    cascade="all, delete-orphan",
    lazy="selectin"
)
```

在 Conversation 模型中：
```python
# 一个 Conversation 属于一个 Agent
agent_id: Mapped[int] = mapped_column(
    ForeignKey("agents.id", ondelete="CASCADE"),
    nullable=False
)

agent: Mapped["Agent"] = relationship(
    "Agent",
    back_populates="conversations"
)
```

### 关系参数说明

| 参数 | 作用 |
|------|------|
| `back_populates` | 双向关系绑定 |
| `cascade="all, delete-orphan"` | 级联删除 |
| `lazy="selectin"` | 加载策略 |
| `ForeignKey` | 外键约束 |
| `ondelete="CASCADE"` | 数据库级联删除 |

---

## 📊 Message 模型

```python
class Message(Base):
    """对话消息模型"""
    
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    # 关系
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )
```

**role 字段的值**：
| 值 | 含义 |
|----|------|
| `user` | 用户发送的消息 |
| `assistant` | AI 回复的消息 |
| `system` | 系统提示消息 |

---

## 🎓 动手练习

### 练习：理解模型关系

回答以下问题：

1. 删除一个 Agent 后，会发生什么？
2. 如何通过 Agent 对象获取所有对话？
3. 如何通过 Message 对象获取所属的 Agent？

**答案**：

```python
# 1. 级联删除：Agent 被删除时，关联的 Conversation 和 Message 都会被删除

# 2. 通过关系访问
agent = await session.get(Agent, 1)
conversations = agent.conversations

# 3. 通过链式访问
message = await session.get(Message, 1)
agent = message.conversation.agent
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 ORM 概念和优势 | ☐ |
| 会使用 Mapped 和 mapped_column | ☐ |
| 理解主键和外键 | ☐ |
| 会定义一对多关系 | ☐ |
| 理解级联删除 | ☐ |
| 理解时间戳自动管理 | ☐ |

---

## 🔜 下一课预告

**第05课：数据库连接与会话管理** - 学习异步数据库连接和事务管理。
