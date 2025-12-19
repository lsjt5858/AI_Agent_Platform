"""
Unified API response schemas.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Schema for error details."""
    
    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details"
    )


class APIResponse(BaseModel, Generic[T]):
    """
    Generic API response wrapper.
    
    Provides consistent response structure for all API endpoints.
    """
    
    success: bool = Field(description="Whether the request was successful")
    data: Optional[T] = Field(
        default=None,
        description="Response data (present on success)"
    )
    error: Optional[ErrorDetail] = Field(
        default=None,
        description="Error information (present on failure)"
    )

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        """Create a successful response."""
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: Optional[dict] = None
    ) -> "APIResponse[None]":
        """Create a failure response."""
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, details=details)
        )
