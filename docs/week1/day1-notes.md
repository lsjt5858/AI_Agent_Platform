# Week 1 - Day 1 - Hello World与路径参数

## 📅 学习日期
日期：2025-12-18
学习时长：2小时

## 🎯 学习目标
- [x] 创建第一个FastAPI应用
- [x] 理解路径参数的使用
- [x] 启动开发服务器
- [x] 查看自动生成的API文档

## 📚 学习内容

### 核心概念
1. **FastAPI应用实例**
   - 定义：FastAPI类的实例是整个API应用的入口
   - 用途：管理路由、中间件、异常处理器等
   - 示例代码：
   ```python
   from fastapi import FastAPI
   app = FastAPI()  # 创建实例
   ```

2. **路径操作装饰器**
   - 定义：`@app.get()`, `@app.post()` 等装饰器
   - 作用：将HTTP方法与路径映射到Python函数
   - 支持的方法：GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD

3. **路径参数**
   - 定义：URL路径中的变量部分
   - 语法：使用花括号 `{}` 在路径中定义
   - 类型提示：使用Python类型提示自动转换和验证

### 关键知识点
- FastAPI基于Starlette和Pydantic构建
- 默认情况下，所有路径参数都视为必需的
- 使用类型提示可以获得：
  - 数据验证
  - 类型转换
  - API文档自动生成
  - IDE智能提示

## 💻 实践代码

### 示例1：创建基本应用
```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()  # 创建实例

@app.get("/")
async def root():
    return {"message": "Hello World!"}
```

**运行结果**：
```json
{
  "message": "Hello World!"
}
```

### 示例2：使用路径参数
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

**测试请求**：
```
GET /items/42
```

**响应**：
```json
{
  "item_id": 42
}
```

## ❓ 遇到的问题

### 问题1：类型提示的作用
**描述**：不太理解为什么要添加 `item_id: int` 的类型提示
**原因分析**：类型提示不仅用于文档，还用于数据验证
**解决方案**：
- 尝试访问 `/items/abc` 看到错误信息
- 查看API文档中的参数类型
```python
# 错误请求会返回：
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "item_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc",
      "url": "https://errors.pydantic.dev/2.5/v/int_parsing"
    }
  ]
}
```

### 问题2：异步 vs 同步函数
**描述**：什么时候使用 async，什么时候不使用？
**解决过程**：
- FastAPI支持两种函数
- 对于简单的操作，同步函数也可以
- 对于I/O密集型操作，异步函数性能更好
- 建议统一使用异步函数以保持一致性

## 💡 学习心得

### 新理解
1. FastAPI的自动文档生成真的很方便
2. 类型提示不仅是最佳实践，还是框架的核心特性
3. 路径参数的自动验证可以避免很多运行时错误

### 容易混淆的概念
- `uvicorn.run(app)` vs 直接运行 `uvicorn main:app`：
  - 前者在代码中启动，适合简单调试
  - 后者是命令行启动，适合开发环境

### 最佳实践
1. 始终为路径参数添加类型提示
2. 使用异步函数作为默认选择
3. 保持路径参数名称清晰有意义
4. 使用热重载模式进行开发

## 📝 知识点总结

### 代码片段备忘
```python
# 创建FastAPI应用
from fastapi import FastAPI
app = FastAPI()

# 定义带路径参数的路由
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app)
```

### 常用命令
```bash
# 启动开发服务器（热重载）
uvicorn week1_qwen.day1:app --reload

# 启动服务器（指定端口）
uvicorn week1_qwen.day1:app --port 8001

# 查看API文档
# 浏览器访问：http://127.0.0.1:8000/docs
```

## 🔗 相关资源
- [FastAPI教程 - 第一步](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [路径参数教程](https://fastapi.tiangolo.com/tutorial/path-params/)

## 📋 下一步计划
- [x] 复习今日内容 ✅
- [ ] 完成练习题：创建个人名片API
- [ ] 预习明日内容：查询参数
- [ ] 尝试添加多个路径参数

## 📈 学习评估
- 理解程度：⭐⭐⭐⭐⭐
- 实践完成度：⭐⭐⭐⭐⭐
- 遇到的困难：异步函数的使用时机
- 解决思路：查询官方文档理解异步编程
- 总结：FastAPI入门比想象中简单，类型提示是核心特性

## 🏆 代码文件
- [`/week1/day1.py`](../../week1_qwen/day12-18.py) - 今日完成的代码