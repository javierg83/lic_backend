from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T = None, message: str = "Operación exitosa") -> "ApiResponse[T]":
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, error: str = None, data: T = None) -> "ApiResponse[T]":
        return cls(success=False, message=message, error=error, data=data)
