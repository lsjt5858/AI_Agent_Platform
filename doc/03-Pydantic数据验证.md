# 第03课：Pydantic 数据验证

## 🎯 本课目标

- 理解 Pydantic 的作用和优势
- 学习定义数据模型（Schema）
- 掌握字段验证和自定义验证器

---

## 📖 什么是 Pydantic？

Pydantic 是 Python 的数据验证库，基于类型提示进行数据校验。

### 核心优势

| 特点 | 说明 |
|------|------|
| 类型安全 | 自动将数据转换为声明的类型 |
| 验证错误 | 提供详细的错误信息 |
| JSON 友好 | 轻松序列化/反序列化 |
| IDE 支持 | 完整的类型提示支持 |

---

## 🔍 项目中的 Schema 设计

项目的数据模式定义在 `app/schemas/` 目录：

```
schemas/
├── __init__.py
├── agent.py         # Agent 相关模式
├── conversation.py  # Conversation 模式
├── message.py       # Message 模式
└── response.py      # 统一响应格式
```

---

## 📝 Agent Schema 详解

查看 `app/schemas/agent.py`：

### 3.1 创建请求模式 (AgentCreate)

```python
from pydantic import BaseModel, Field, field_validator

class AgentCreate(BaseModel):
    """创建新智能体的模式"""

    name: str = Field(
        ...,                          # ... 表示必填
        min_length=1,
        max_length=100,
        description="智能体名称，必填且非空"
    )
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="定义智能体行为的系统提示"
    )
    description: Optional[str] = Field(
        default=None,
        description="可选的智能体描述"
    )
```

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | str | ✅ | 智能体名称，1-100字符 |
| `system_prompt` | str | ❌ | 系统提示，有默认值 |
| `description` | str \| None | ❌ | 可选描述 |

### 3.2 Field 参数详解

```python
Field(
    ...,                    # 默认值，... 表示必填
    min_length=1,          # 最小长度
    max_length=100,        # 最大长度
    description="描述文字"  # 字段描述（用于文档）
)
```

| 参数 | 作用 |
|------|------|
| `...` | 必填字段标记 |
| `default=xxx` | 设置默认值 |
| `min_length` | 字符串最小长度 |
| `max_length` | 字符串最大长度 |
| `ge`, `le` | 数值范围（大于等于/小于等于）|
| `description` | 字段描述 |

### 3.3 自定义验证器

```python
@field_validator("name")
@classmethod
def name_must_not_be_whitespace(cls, v: str) -> str:
    """验证名称不能只是空白字符"""
    if not v.strip():
        raise ValueError("智能体名称不能为空或仅包含空白字符")
    return v.strip()  # 返回去除首尾空格的值
```

**验证逻辑**：
1. 接收字段值 `v`
2. 检查去除空格后是否为空
3. 如果为空，抛出 `ValueError`
4. 返回处理后的值（自动去除空格）

---

## 📤 更新请求模式 (AgentUpdate)

```python
class AgentUpdate(BaseModel):
    """更新现有智能体的模式"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    system_prompt: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
```

> 💡 **与 Create 的区别**  
> Update 模式中所有字段都是 `Optional`，这样可以只更新部分字段。

---

## 📥 响应模式 (AgentResponse)

```python
class AgentResponse(BaseModel):
    """智能体 API 响应的模式"""

    id: int
    name: str
    system_prompt: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

**重要配置**：

```python
model_config = {"from_attributes": True}
```

这个配置允许从 ORM 对象创建 Pydantic 模型：

```python
# 将 SQLAlchemy 模型转换为响应模式
agent = await service.get_agent(agent_id)
response = AgentResponse.model_validate(agent)
```

---

## 🌐 统一响应格式

查看 `app/schemas/response.py`：

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """通用 API 响应包装器"""

    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        """创建成功响应"""
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str) -> "APIResponse[None]":
        """创建失败响应"""
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message)
        )
```

### 使用示例

```python
# 成功响应
return APIResponse.ok(AgentResponse.model_validate(agent))

# 失败响应
return APIResponse.fail("NOT_FOUND", "Agent not found")
```

### 响应格式示例

**成功**：
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "小助手",
    "system_prompt": "You are a helpful assistant."
  },
  "error": null
}
```

**失败**：
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Agent with id 999 not found"
  }
}
```

---

## 🎓 动手练习

### 练习：创建消息验证

```python
from pydantic import BaseModel, Field, field_validator

class MessageCreate(BaseModel):
    """发送消息的请求模式"""
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="消息内容"
    )
    
    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("消息内容不能为空")
        return v.strip()
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 Pydantic 的作用 | ☐ |
| 会使用 BaseModel 定义模式 | ☐ |
| 会使用 Field 设置字段约束 | ☐ |
| 会编写自定义验证器 | ☐ |
| 理解 Create/Update/Response 的区别 | ☐ |
| 理解统一响应格式的设计 | ☐ |

---

## 🔜 下一课预告

**第04课：SQLAlchemy ORM 模型设计** - 学习如何设计数据库模型。
