"""
FastAPI application entry point.
Configures CORS, exception handlers, and static file serving.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import init_db
from .routers import agents_router, conversations_router, messages_router

settings = get_settings()

# Get the project root directory (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown (if needed)


app = FastAPI(
    title=settings.app_name,
    description="AI Agent 对话平台 - 创建和管理多个 AI 智能体",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Custom exception classes
class NotFoundError(Exception):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Validation error exception."""

    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class LLMError(Exception):
    """LLM API error exception."""

    def __init__(self, message: str = "LLM API error"):
        self.message = message
        super().__init__(self.message)


class TimeoutError(Exception):
    """Timeout error exception."""

    def __init__(self, message: str = "Request timed out"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(Exception):
    """Database operation error exception."""

    def __init__(self, message: str = "Database operation failed"):
        self.message = message
        super().__init__(self.message)


# Global exception handlers
@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle 404 Not Found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "NOT_FOUND",
                "message": exc.message,
            },
        },
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle 422 Validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(LLMError)
async def llm_exception_handler(request: Request, exc: LLMError):
    """Handle 502 LLM API errors."""
    return JSONResponse(
        status_code=502,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "LLM_ERROR",
                "message": exc.message,
            },
        },
    )


@app.exception_handler(TimeoutError)
async def timeout_exception_handler(request: Request, exc: TimeoutError):
    """Handle 504 Timeout errors."""
    return JSONResponse(
        status_code=504,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "TIMEOUT_ERROR",
                "message": exc.message,
            },
        },
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle 500 Database errors."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "DATABASE_ERROR",
                "message": exc.message,
            },
        },
    )


# Register API routers with /api prefix
app.include_router(agents_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(messages_router, prefix="/api")

# Mount static files directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """根路径 - 提供前端页面。"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "欢迎使用 AI Agent 对话平台"}


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {
        "success": True,
        "data": {"status": "healthy"},
        "error": None,
    }
