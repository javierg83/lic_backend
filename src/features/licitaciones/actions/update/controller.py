from fastapi import APIRouter
from uuid import UUID
from .schemas import LicitacionUpdate, LicitacionUpdateResponse
from .service import LicitacionUpdateService
from src.core.responses import ApiResponse

router = APIRouter()

@router.put("/{id}", response_model=ApiResponse[LicitacionUpdateResponse])
async def update_licitacion(id: UUID, data: LicitacionUpdate):
    return await LicitacionUpdateService.process(id, data)
