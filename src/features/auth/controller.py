from fastapi import APIRouter
from .schemas import LoginData
from .service import AuthService

from src.core.responses import ApiResponse

router = APIRouter()

@router.post("/login", response_model=ApiResponse)
def login(data: LoginData):
    result = AuthService.login(data)
    return ApiResponse.ok(data=result, message="Login exitoso")
