from fastapi import APIRouter
from .service import LicitacionListService
from .schemas import LicitacionListResponse
from src.core.responses import ApiResponse

router = APIRouter()

@router.get("/list", response_model=ApiResponse[LicitacionListResponse])
async def list_licitaciones():
    return await LicitacionListService.process()
