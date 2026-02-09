from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="성공 여부")
    status_code: str = Field(..., description="응답 코드 (예: SUCCESS, ERROR_001)")
    message: str = Field(..., description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")

    @classmethod
    def success_response(cls, data: T = None, message: str = "Request successful"):
        return cls(success=True, status_code="SUCCESS", message=message, data=data)

    @classmethod
    def error_response(cls, code: str, message: str, data: Optional[T] = None):
        return cls(success=False, status_code=code, message=message, data=data)
