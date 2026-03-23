from uuid import UUID
from fastapi import APIRouter, Body
from src.core.responses import ApiResponse
from .schemas import EntregaUpdate
from ..show.schemas import EntregaShowResponse
from .service import EntregaUpdateService

router = APIRouter()

@router.put('/{licitacion_id}/entregas', response_model=ApiResponse[EntregaShowResponse])
async def update_entrega(licitacion_id: UUID, data: EntregaUpdate = Body(...)):
    try:
        return await EntregaUpdateService.process(licitacion_id, data)
    except Exception as e:
        return ApiResponse.fail(message=str(e))
