"""
Unified API response schemas.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """错误详情的模式。"""

    code: str = Field(description="错误代码")
    message: str = Field(description="人类可读的错误消息")
    details: Optional[dict] = Field(
        default=None,
        description="额外的错误详情"
    )


class APIResponse(BaseModel, Generic[T]):
    """
    通用API响应包装器。

    为所有API端点提供一致的响应结构。
    """

    success: bool = Field(description="请求是否成功")
    data: Optional[T] = Field(
        default=None,
        description="响应数据（成功时存在）"
    )
    error: Optional[ErrorDetail] = Field(
        default=None,
        description="错误信息（失败时存在）"
    )

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        """创建成功的响应。"""
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None
    ) -> "APIResponse[None]":
        """创建失败的响应。"""
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, details=details)
        )
