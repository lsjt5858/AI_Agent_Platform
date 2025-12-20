# 第06课：Repository 数据访问层

## 🎯 本课目标

- 理解 Repository 模式的设计理念
- 学习 CRUD 操作的封装
- 掌握 SQLAlchemy 异步查询语法

---

## 📖 什么是 Repository 模式？

Repository（仓库）模式是一种**数据访问抽象层**，将数据库操作封装在独立的类中。

### 优势

| 优势 | 说明 |
|------|------|
| 解耦 | 业务逻辑与数据访问分离 |
| 可测试 | 易于进行单元测试 |
| 可维护 | 数据访问逻辑集中管理 |
| 可替换 | 更换数据库时只需修改 Repository |

### 架构位置

```
Router (API层)
    │
    ▼
Service (业务逻辑层)
    │
    ▼
Repository (数据访问层)  ← 本课重点
    │
    ▼
Database (数据库)
```

---

## 📝 AgentRepository 详解

查看 `app/repositories/agent.py`：

### 1. 类结构

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.agent import Agent
from ..schemas.agent import AgentCreate, AgentUpdate

class AgentRepository:
    """Agent 数据访问类"""

    def __init__(self, session: AsyncSession):
        """初始化时注入数据库会话"""
        self.session = session
```

### 2. Create - 创建

```python
async def create(self, data: AgentCreate) -> Agent:
    """创建新的 Agent"""
    agent = Agent(
        name=data.name,
        system_prompt=data.system_prompt,
        description=data.description
    )
    self.session.add(agent)           # 添加到会话
    await self.session.flush()        # 执行 INSERT
    await self.session.refresh(agent) # 刷新获取 id
    return agent
```

**关键点**：
- `add()` - 将对象标记为待插入
- `flush()` - 执行 SQL 但不提交事务
- `refresh()` - 重新从数据库加载对象（获取自动生成的 id）

### 3. Read - 查询

#### 查询所有

```python
async def get_all(self) -> List[Agent]:
    """获取所有 Agent，按创建时间降序"""
    result = await self.session.execute(
        select(Agent).order_by(Agent.created_at.desc())
    )
    return list(result.scalars().all())
```

**查询语法解析**：

```python
select(Agent)                      # SELECT * FROM agents
    .order_by(Agent.created_at.desc())  # ORDER BY created_at DESC

result = await session.execute(query)  # 执行查询
result.scalars()                       # 获取模型对象
result.scalars().all()                 # 转为列表
```

#### 按 ID 查询

```python
async def get_by_id(self, agent_id: int) -> Optional[Agent]:
    """根据 ID 获取 Agent"""
    result = await self.session.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    return result.scalar_one_or_none()
```

**方法对比**：

| 方法 | 返回值 | 无结果时 |
|------|--------|---------|
| `scalar_one()` | 单个对象 | 抛异常 |
| `scalar_one_or_none()` | 单个对象或 None | 返回 None |
| `scalars().all()` | 列表 | 返回空列表 |

### 4. Update - 更新

```python
async def update(self, agent_id: int, data: AgentUpdate) -> Optional[Agent]:
    """更新 Agent"""
    agent = await self.get_by_id(agent_id)
    if agent is None:
        return None

    # 只更新提供的字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(agent, field, value)

    await self.session.flush()
    await self.session.refresh(agent)
    return agent
```

**关键技术**：

```python
# model_dump(exclude_unset=True) 
# 只获取用户明确传入的字段，忽略未设置的
data = AgentUpdate(name="新名称")
data.model_dump(exclude_unset=True)  # {'name': '新名称'}
# description 未传入，不会出现在结果中
```

### 5. Delete - 删除

```python
async def delete(self, agent_id: int) -> bool:
    """删除 Agent"""
    agent = await self.get_by_id(agent_id)
    if agent is None:
        return False

    await self.session.delete(agent)
    await self.session.flush()
    return True
```

---

## 📊 MessageRepository

查看 `app/repositories/message.py`：

```python
class MessageRepository:
    """Message 数据访问类"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, 
        conversation_id: int, 
        role: str, 
        content: str
    ) -> Message:
        """创建新消息"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_by_conversation(
        self, 
        conversation_id: int
    ) -> List[Message]:
        """获取对话的所有消息，按时间升序"""
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())
```

---

## 🔧 常用查询语法

### 条件查询

```python
# WHERE 条件
select(Agent).where(Agent.name == "小助手")

# 多条件 AND
select(Agent).where(
    Agent.name == "小助手",
    Agent.id > 10
)

# OR 条件
from sqlalchemy import or_
select(Agent).where(
    or_(Agent.name == "A", Agent.name == "B")
)

# LIKE 模糊查询
select(Agent).where(Agent.name.like("%助手%"))
```

### 排序和分页

```python
# 排序
select(Agent).order_by(Agent.created_at.desc())

# 分页
select(Agent).offset(10).limit(20)  # 跳过10条，取20条
```

### 聚合查询

```python
from sqlalchemy import func

# COUNT
result = await session.execute(
    select(func.count()).select_from(Agent)
)
count = result.scalar()
```

---

## 🎓 动手练习

### 练习：添加搜索功能

在 `AgentRepository` 中添加按名称搜索：

```python
async def search_by_name(self, keyword: str) -> List[Agent]:
    """按名称模糊搜索 Agent"""
    result = await self.session.execute(
        select(Agent)
        .where(Agent.name.like(f"%{keyword}%"))
        .order_by(Agent.created_at.desc())
    )
    return list(result.scalars().all())
```

---

## 📋 Repository 设计原则

| 原则 | 说明 |
|------|------|
| 单一职责 | 每个 Repository 只负责一个模型 |
| 接收会话 | 通过构造函数注入 session |
| 不提交事务 | 只做 flush，不做 commit |
| 返回模型对象 | 返回 ORM 对象，不返回原始数据 |

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 Repository 模式的优势 | ☐ |
| 会实现 CRUD 操作 | ☐ |
| 掌握 select 查询语法 | ☐ |
| 理解 flush vs commit 的区别 | ☐ |
| 会使用条件查询和排序 | ☐ |

---

## 🔜 下一课预告

**第07课：Service 业务逻辑层** - 学习如何在 Service 层组织业务逻辑。
