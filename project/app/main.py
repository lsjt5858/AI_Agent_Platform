"""
FastAPI application entry point.
Configures CORS, exception handlers, and static file serving.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AI Agent 对话平台 - 创建和管理多个 AI 智能体",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


# Mount static files directory
app.mount("/static", StaticFiles(directory="project/static"), name="static")


@app.get("/")
async def root():
    """Root endpoint - redirect to docs or serve frontend."""
    return {
        "success": True,
        "data": {
            "message": f"Welcome to {settings.app_name}",
            "docs": "/docs",
            "version": "1.0.0",
        },
        "error": None,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "data": {"status": "healthy"},
        "error": None,
    }
