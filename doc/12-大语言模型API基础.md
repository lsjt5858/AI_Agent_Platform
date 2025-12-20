# 第12课：大语言模型 API 基础

## 🎯 本课目标

- 了解 OpenAI 兼容 API 的接口规范
- 理解 Chat Completion API 的使用方法
- 学习消息格式和参数配置

---

## 📖 什么是 LLM API？

大语言模型（LLM）API 允许我们通过 HTTP 请求与 AI 模型交互。

### 常见的 LLM 服务

| 服务 | 提供商 | 特点 |
|------|--------|------|
| 通义千问 | 阿里云 | 国内访问稳定，价格较低 |
| OpenAI | OpenAI | 模型能力强，需科学上网 |
| DeepSeek | DeepSeek | 性价比高，支持长上下文 |
| 文心一言 | 百度 | 国内服务，中文较好 |

### OpenAI 兼容接口

大多数 LLM 服务都提供与 OpenAI 兼容的 API 接口，格式统一：

```
POST /v1/chat/completions
```

---

## 🔍 API 请求格式

### 请求结构

```python
POST https://api.example.com/v1/chat/completions

Headers:
    Authorization: Bearer sk-xxxxx
    Content-Type: application/json

Body:
{
    "model": "qwen-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000
}
```

### 关键参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | str | 模型名称，如 "qwen-turbo" |
| `messages` | list | 对话消息列表 |
| `temperature` | float | 随机性，0-2，越高越随机 |
| `max_tokens` | int | 最大输出 token 数 |

### 消息角色

| 角色 | 用途 |
|------|------|
| `system` | 系统提示，定义 AI 的行为和人设 |
| `user` | 用户发送的消息 |
| `assistant` | AI 的回复 |

---

## 📝 响应格式

```json
{
    "id": "chatcmpl-xxxxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "qwen-turbo",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "你好！有什么可以帮助你的吗？"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 15,
        "total_tokens": 35
    }
}
```

### 响应字段说明

| 字段 | 说明 |
|------|------|
| `choices[0].message.content` | AI 的回复内容 |
| `choices[0].finish_reason` | 结束原因（stop/length/...）|
| `usage.prompt_tokens` | 输入消耗的 token |
| `usage.completion_tokens` | 输出消耗的 token |
| `usage.total_tokens` | 总 token 消耗 |

---

## 🔧 项目中的 LLM 封装

查看 `app/services/llm.py`：

### 格式化消息

```python
def format_messages_for_llm(
    messages: list[dict[str, str]],
    system_prompt: str
) -> list[dict[str, str]]:
    """
    将消息格式化为 LLM API 需要的格式
    """
    formatted = []
    
    # 1. 添加系统提示
    if system_prompt:
        formatted.append({
            "role": "system",
            "content": system_prompt
        })
    
    # 2. 添加对话消息
    for msg in messages:
        formatted.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    return formatted
```

**示例变换**：

输入：
```python
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"},
    {"role": "user", "content": "今天天气如何？"}
]
system_prompt = "你是一个天气助手"
```

输出：
```python
[
    {"role": "system", "content": "你是一个天气助手"},
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！"},
    {"role": "user", "content": "今天天气如何？"}
]
```

### 解析响应

```python
def parse_llm_response(response_data: dict) -> tuple[str, dict[str, int]]:
    """
    解析 LLM API 响应
    
    Returns:
        (回复内容, token使用统计)
    """
    try:
        choices = response_data.get("choices", [])
        if not choices:
            raise LLMAPIError("No choices in response")
        
        # 提取回复内容
        message = choices[0].get("message", {})
        content = message.get("content")
        
        if content is None:
            raise LLMAPIError("No content in message")
        
        # 提取 token 使用
        usage = response_data.get("usage", {})
        token_usage = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
        
        return content, token_usage
        
    except (KeyError, IndexError) as e:
        raise LLMAPIError(f"Failed to parse response: {e}")
```

---

## 📊 Temperature 参数详解

```
Temperature = 0.0 (确定性)
┌───────────────────────────────────────┐
│ 同样的输入，每次输出几乎相同           │
│ 适合：事实查询、代码生成               │
└───────────────────────────────────────┘

Temperature = 0.7 (平衡，默认)
┌───────────────────────────────────────┐
│ 在质量和多样性之间取得平衡             │
│ 适合：一般对话、问答                   │
└───────────────────────────────────────┘

Temperature = 1.5+ (高创造性)
┌───────────────────────────────────────┐
│ 输出更加随机、有创意                   │
│ 适合：创意写作、头脑风暴               │
└───────────────────────────────────────┘
```

---

## 🎓 cURL 测试示例

```bash
curl https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-turbo",
    "messages": [
      {"role": "system", "content": "你是一个有帮助的助手"},
      {"role": "user", "content": "请用一句话介绍 Python"}
    ]
  }'
```

---

## 📋 Token 计费说明

| 概念 | 说明 |
|------|------|
| Token | 文本的最小单位，中文约1字=1token |
| prompt_tokens | 输入消耗的 token（包括历史消息）|
| completion_tokens | 输出消耗的 token |
| 计费 | 通常按 token 数量计费 |

### Token 估算

| 语言 | 大约比例 |
|------|---------|
| 英文 | 1 token ≈ 4 个字符 |
| 中文 | 1 token ≈ 1-2 个字符 |

---

## 🔒 API Key 安全

```python
# ❌ 错误：硬编码在代码中
api_key = "sk-xxxxxxxxxxxx"

# ✅ 正确：从环境变量读取
import os
api_key = os.environ.get("LLM_API_KEY")

# ✅ 更好：使用配置管理
from .config import get_settings
settings = get_settings()
api_key = settings.llm_api_key
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解 OpenAI 兼容 API 格式 | ☐ |
| 理解消息角色（system/user/assistant）| ☐ |
| 理解 temperature 参数作用 | ☐ |
| 理解 token 概念和计费 | ☐ |
| 会使用 cURL 测试 API | ☐ |

---

## 🔜 下一课预告

**第13课：异步 HTTP 客户端** - 学习使用 httpx 进行异步 API 调用。
