# 第13课：异步 HTTP 客户端

## 🎯 本课目标

- 理解为什么使用异步 HTTP 客户端
- 学习 httpx 的使用方法
- 掌握超时和错误处理

---

## 📖 为什么用 httpx？

### requests vs httpx

| 特性 | requests | httpx |
|------|----------|-------|
| 同步支持 | ✅ | ✅ |
| 异步支持 | ❌ | ✅ |
| HTTP/2 | ❌ | ✅ |
| 现代化 | 较老 | 新设计 |

### 异步的优势

```python
# 同步方式 - 串行执行，等待阻塞
response1 = requests.get(url1)  # 等待...
response2 = requests.get(url2)  # 等待...
# 总时间 = 时间1 + 时间2

# 异步方式 - 并发执行
response1, response2 = await asyncio.gather(
    client.get(url1),
    client.get(url2)
)
# 总时间 ≈ max(时间1, 时间2)
```

---

## 🔍 LLMService 异步请求

查看 `app/services/llm.py`：

### 服务类初始化

```python
class LLMService:
    """LLM API 服务"""
    
    def __init__(
        self,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: int = 2
    ):
        settings = get_settings()
        
        self.api_base_url = api_base_url or settings.llm_api_base_url
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.timeout = timeout or settings.llm_timeout
        self.max_retries = max_retries
        
        # 移除末尾斜杠
        self.api_base_url = self.api_base_url.rstrip("/")
```

### 构建请求头

```python
def _get_headers(self) -> dict[str, str]:
    """获取 HTTP 请求头"""
    headers = {
        "Content-Type": "application/json",
    }
    if self.api_key:
        headers["Authorization"] = f"Bearer {self.api_key}"
    return headers
```

### 构建请求体

```python
def _build_request_body(
    self,
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> dict[str, Any]:
    """构建 API 请求体"""
    body = {
        "model": self.model,
        "messages": messages,
        "temperature": temperature,
    }
    
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
        
    return body
```

---

## 📝 异步请求实现

```python
async def _make_request(
    self,
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> dict[str, Any]:
    """发送异步 HTTP 请求"""
    
    url = f"{self.api_base_url}/chat/completions"
    headers = self._get_headers()
    body = self._build_request_body(messages, temperature, max_tokens)
    
    # 使用异步上下文管理器
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        try:
            # 发送 POST 请求
            response = await client.post(
                url, 
                headers=headers, 
                json=body
            )
            
            # 检查状态码
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", error_detail)
                except:
                    pass
                
                raise LLMAPIError(
                    f"LLM API error: {error_detail}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except httpx.TimeoutException as e:
            logger.error(f"LLM API timeout: {e}")
            raise LLMTimeoutError(
                f"Request timed out after {self.timeout} seconds"
            )
        except httpx.RequestError as e:
            logger.error(f"LLM API request error: {e}")
            raise LLMAPIError(f"Request failed: {str(e)}")
```

### 关键点解析

```python
# 1. 异步上下文管理器
async with httpx.AsyncClient(timeout=30) as client:
    # client 会在退出时自动关闭

# 2. 异步 POST 请求
response = await client.post(url, headers=headers, json=body)

# 3. json 参数会自动
#    - 将 dict 序列化为 JSON
#    - 设置 Content-Type: application/json

# 4. 异常处理
# TimeoutException - 超时
# RequestError - 网络错误
```

---

## 🔄 重试机制

```python
async def chat(
    self,
    messages: list[dict[str, str]],
    system_prompt: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> tuple[str, dict[str, int]]:
    """发送聊天请求，支持重试"""
    
    formatted_messages = format_messages_for_llm(messages, system_prompt)
    last_error = None
    
    # 重试循环
    for attempt in range(self.max_retries + 1):
        try:
            response_data = await self._make_request(
                formatted_messages,
                temperature,
                max_tokens
            )
            return parse_llm_response(response_data)
            
        except LLMTimeoutError:
            # 超时不重试
            raise
            
        except LLMAPIError as e:
            last_error = e
            # 只重试 5xx 服务器错误
            if e.status_code and 500 <= e.status_code < 600:
                if attempt < self.max_retries:
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries}")
                    continue
            # 4xx 客户端错误不重试
            raise
            
        except Exception as e:
            last_error = e
            if attempt < self.max_retries:
                logger.warning(f"Unexpected error, retrying: {e}")
                continue
            raise LLMAPIError(f"Unexpected error: {str(e)}")
    
    if last_error:
        raise last_error
```

### 重试策略

```
请求失败
    │
    ▼
判断错误类型
    │
    ├── TimeoutException → 不重试，直接抛出
    │
    ├── 5xx 服务器错误 → 重试（最多 N 次）
    │
    ├── 4xx 客户端错误 → 不重试，直接抛出
    │
    └── 其他错误 → 重试（最多 N 次）
```

---

## 📊 httpx 常用操作

### 基本请求

```python
import httpx

# GET 请求
async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/data")
    data = response.json()

# POST 请求（JSON）
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.example.com/data",
        json={"key": "value"}
    )

# POST 请求（表单）
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.example.com/form",
        data={"field": "value"}
    )
```

### 设置超时

```python
# 全局超时
client = httpx.AsyncClient(timeout=30.0)

# 细粒度超时
timeout = httpx.Timeout(
    connect=5.0,    # 连接超时
    read=30.0,      # 读取超时
    write=10.0,     # 写入超时
    pool=10.0       # 连接池超时
)
client = httpx.AsyncClient(timeout=timeout)
```

### 设置请求头

```python
headers = {
    "Authorization": "Bearer token",
    "User-Agent": "MyApp/1.0"
}
async with httpx.AsyncClient(headers=headers) as client:
    response = await client.get(url)
```

---

## 🎓 动手练习

### 练习：添加请求日志

```python
import logging
import time

logger = logging.getLogger(__name__)

async def _make_request_with_logging(self, ...):
    """带日志的请求"""
    
    start_time = time.time()
    logger.info(f"Calling LLM API: {self.model}")
    
    try:
        response = await self._make_request(...)
        elapsed = time.time() - start_time
        logger.info(f"LLM response received in {elapsed:.2f}s")
        return response
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM request failed after {elapsed:.2f}s: {e}")
        raise
```

---

## 📝 本课小结

| 知识点 | 掌握程度 |
|--------|---------|
| 理解异步 HTTP 的优势 | ☐ |
| 会使用 httpx.AsyncClient | ☐ |
| 理解超时配置 | ☐ |
| 会处理各类异常 | ☐ |
| 理解重试策略 | ☐ |

---

## 🔜 下一课预告

**第14课：对话上下文管理** - 学习如何管理多轮对话的上下文。
