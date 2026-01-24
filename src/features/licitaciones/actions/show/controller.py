from fastapi import APIRouter
from uuid import UUID
from .service import LicitacionShowService
from .schemas import LicitacionShowResponse
from src.core.responses import ApiResponse

router = APIRouter()

@router.get("/{licitacion_id}", response_model=ApiResponse[LicitacionShowResponse])
async def show_licitacion(licitacion_id: UUID):
    return await LicitacionShowService.process(licitacion_id)
