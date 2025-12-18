#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/12/18
# @Description: [对文件功能等的简要描述（可自行添加）]
import uvicorn
from  fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
# ============================================================================
# 核心功能：Item类（Pydantic BaseModel）既用来定义接口入参的结构、类型和必填 / 可选规则，也用来严格限制入参的合法性，不符合规则的请求会被直接拦截并返回错误。
# 附加功能：还能自动解析请求体、生成 API 文档、规范返回数据格式，这也是 FastAPI 高效的重要原因。
# 关键区别：它不仅是 “入参定义”，还能用于 “出参规范”，是 FastAPI 中处理数据校验和序列化的核心工具。
# Pydantic 模型是 FastAPI 的核心，用于数据验证和序列化：  ✅


# 定义数据模型=============================
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

# {
#   "name": "测试商品",  // 替换成实际名称
#   "price": 19.9,      // 必填的float类型
#   "description": "这是测试商品",  // 可选
#   "tax": 1.2          // 可选
# }


# 使用模型作为请求体==============================
@app.post("/items/")
async def create_item(item: Item):
    return item


# 模型也可用于响应==============================
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    # 从数据库获取数据  此处为示例
    return {
        "item_id": item_id,
        "item_name": "<NAME>",
        "item_description": None,
        "item_tax_amount": None,
    }


# 模型还可用于嵌套==============================
class user(BaseModel):
    username: str
    full_name: Optional[str] = None
    items: list[Item] = []


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)