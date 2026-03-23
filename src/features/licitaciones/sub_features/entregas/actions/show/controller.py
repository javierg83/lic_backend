from uuid import UUID
from fastapi import APIRouter
from src.core.responses import ApiResponse
from .schemas import EntregaShowResponse
from .service import EntregaShowService

router = APIRouter()

@router.get('/{licitacion_id}/entregas', response_model=ApiResponse[EntregaShowResponse])
async def get_entrega(licitacion_id: UUID):
    try:
        return await EntregaShowService.process(licitacion_id)
    except Exception as e:
        return ApiResponse.fail(message=str(e))
