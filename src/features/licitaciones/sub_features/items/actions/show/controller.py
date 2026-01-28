from fastapi import APIRouter
from .service import ItemsLicitacionShowService
from .schemas import ItemsLicitacionListResponse
from src.core.responses import ApiResponse

router = APIRouter(prefix="/{licitacion_id}/items", tags=["items"])

@router.get("", response_model=ApiResponse[ItemsLicitacionListResponse])
async def get_items(licitacion_id: str):
    return await ItemsLicitacionShowService.process(licitacion_id)
