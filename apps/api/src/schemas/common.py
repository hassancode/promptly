"""Common Pydantic schemas for API responses"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper"""

    success: bool = True
    data: T
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    error: str
    status_code: int
    details: Optional[Any] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""

    items: List[T]
    total: int
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, page: int, page_size: int):
        """Create paginated response"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: Optional[str] = None
