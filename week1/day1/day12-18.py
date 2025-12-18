#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 熊🐻来个🥬
# @Date:  2025/12/18
# @Description: [对文件功能等的简要描述（可自行添加）]
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse

app = FastAPI()  # 创建实例

# 用全局字典临时存储item（实际项目用数据库）
items_db = {}
# ============================================================================
@app.get("/items")
async def root():
    return {"message": "Hello World!"}


@app.post("/items/")
async def create_item(item: dict):
    item_id = item.get("item_id")
    if item_id:
        items_db[item_id] = item
        return {"message": "创建成功以下是创建的数据", "item": item}
    return {"message": "缺少item_id"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


#  @app.get(...) 路径操作装饰器   定义请求方法和路径
#  async  def   声明异步函数, 但可以使用普通函数
# item_id: int  路径参数    带有类型声明  声明类型如下比如以下类型：  int float bool  bytes

# 返回值默认转换为 JSON
# 路径 为    客户端请求 → FastAPI 路由 → 路径参数解析 → 函数执行 → 响应生成
# 请求路由的知识点:
#     1: 请求路径后带 / 的路由,  默认请求时不带 / 的话,系统会默认重定向到 带/的路由, 然后带/直接访问也是OK的
#     2: 请求路径后不带 / 的路由, 默认请求时不带/ 正常返回,带上/ 的话就会 404


# ==============================响应格式==============================================
# JSON 响应（默认）
@app.get("/json")
async def json_response():
    return {"message": "This is JSON"}


# HTML 响应
@app.get("/html", response_class=HTMLResponse)
async def html_response():
    return """
    <html>
        <body>
            <h1>Hello HTML Response</h1>
            <p>This is rendered as HTML</p>
        </body>
    </html>
    """


# 重定向
@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="/json")


# 自定义状态码
@app.get("/status")
async def custom_status():
    return JSONResponse(
        content={"message": "Created successfully"},
        status_code=201
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
