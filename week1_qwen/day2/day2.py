#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/12/18
# @Description: FastAPI Day 2 - 请求方法与查询参数

import uvicorn
from fastapi import FastAPI, Query
from typing import Optional, List

app = FastAPI()  # 创建实例

# 模拟的TODO数据
fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
    {"item_name": "Wux"},
]

# ===== GET请求示例 =====

@app.get("/")
async def root():
    """根路径，返回欢迎信息"""
    return {"message": "Welcome to FastAPI Day 2!"}

# 路径参数示例（复习Day 1）
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """根据ID获取单个物品"""
    return {"item_id": item_id, "item_name": f"Item {item_id}"}

# 查询参数示例
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    """
    获取物品列表，支持分页

    参数:
    - skip: 跳过的项目数（默认0）
    - limit: 返回的最大项目数（默认10）
    """
    return fake_items_db[skip : skip + limit]

# 可选查询参数
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: int, q: Optional[str] = None, short: bool = False
):
    """
    读取用户的物品

    参数:
    - user_id: 用户ID（路径参数）
    - item_id: 物品ID（路径参数）
    - q: 查询字符串（可选查询参数）
    - short: 是否返回简短描述（布尔查询参数）
    """
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

# 多个查询参数
@app.get("/search/items")
async def search_items(
    q: Optional[str] = Query(None, min_length=3, max_length=50),
    skip: int = Query(0, ge=0, description="要跳过的项目数量"),
    limit: int = Query(10, ge=1, le=100, description="要返回的最大项目数"),
    category: Optional[str] = Query(None, alias="cat"),
):
    """
    搜索物品

    参数:
    - q: 搜索关键词，最小3个字符，最大50个字符
    - skip: 跳过的项目数，必须大于等于0
    - limit: 返回的项目数，必须在1-100之间
    - category: 物品分类（别名cat）
    """
    results = {
        "items": [{"item_id": "Foo"}, {"item_id": "Bar"}],
        "query": q,
        "skip": skip,
        "limit": limit,
        "category": category,
    }
    return results

# 列表类型的查询参数
@app.get("/items/filter")
async def filter_items(
    ids: List[int] = Query([], description="要筛选的物品ID列表")
):
    """
    根据ID列表筛选物品

    示例: /items/filter?ids=1&ids=2&ids=3
    """
    return {"selected_ids": ids}

# ===== POST请求示例 =====

from pydantic import BaseModel, HttpUrl

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []

@app.post("/items/")
async def create_item(item: Item):
    """
    创建新物品

    接收JSON格式的请求体，自动验证数据
    """
    return item

# ===== PUT请求示例 =====

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    更新物品信息

    参数:
    - item_id: 路径参数，要更新的物品ID
    - item: 请求体，包含更新后的物品信息
    """
    return {"item_id": item_id, "item": item}

# ===== DELETE请求示例 =====

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """
    删除物品

    参数:
    - item_id: 要删除的物品ID
    """
    return {"message": f"Item {item_id} deleted successfully"}

# ===== 综合示例：TODO API =====

class TodoItem(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

# 模拟的TODO数据库
todos = [
    {"id": 1, "title": "学习FastAPI", "description": "完成FastAPI教程", "completed": True},
    {"id": 2, "title": "编写代码", "description": "完成今天的练习", "completed": False},
]

@app.get("/todos/", response_model=List[TodoItem])
async def get_todos(completed: Optional[bool] = None):
    """
    获取TODO列表

    参数:
    - completed: 可选，筛选已完成/未完成的任务
    """
    if completed is not None:
        return [todo for todo in todos if todo["completed"] == completed]
    return todos

@app.post("/todos/", response_model=TodoItem)
async def create_todo(todo: TodoItem):
    """
    创建新的TODO项
    """
    new_id = max(todo["id"] for todo in todos) + 1 if todos else 1
    todo_dict = todo.dict()
    todo_dict["id"] = new_id
    todos.append(todo_dict)
    return todo

@app.get("/todos/{todo_id}", response_model=TodoItem)
async def get_todo(todo_id: int):
    """
    获取单个TODO项
    """
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return {"error": "Todo not found"}, 404

if __name__ == "__main__":
    uvicorn.run("week1_qwen.day2.day2:app", host="127.0.0.1", port=8000, reload=True)
    # uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)