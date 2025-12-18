#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/12/18
# @Description: [对文件功能等的简要描述（可自行添加）]
from typing import List

import uvicorn
# 1. 创建一个图书管理 API
# 2. 实现获取所有图书和按ID获取单本图书的功能
# 3. 使用 Pydantic 模型定义图书结构
# 4. 确保能通过自动生成的文档访问和测试 API
# 提示

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, HTTPException, HTTPException


app = FastAPI()

# ==================================

class Books(BaseModel):
    book_name: str
    book_id: int
    book_description: str
    book_author: str
    book_price: float
    is_china: bool

books_db = [
    Books(book_name='FastAPI入门', book_id=1, book_description="张三", book_author="张三2023",book_price=19.9,is_china=True),
    Books(book_name='Python进阶', book_id=2, book_description="三", book_author="20张三23",book_price=19.9,is_china=True),
    Books(book_name='Python进阶Python进阶', book_id=3, book_description="张", book_author="张三20张三23张三",book_price=19.9,is_china=True),
]

@app.get("/books/")
async def get_books():
    return books_db


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books_db:
        if book.book_id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)



