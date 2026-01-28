from fastapi import APIRouter
from .service import ItemLicitacionUpdateService
from .schemas import ItemLicitacionUpdate, ItemLicitacionUpdateResponse
from src.core.responses import ApiResponse

router = APIRouter(prefix="/items", tags=["items"])

@router.put("/{item_id}", response_model=ApiResponse[ItemLicitacionUpdateResponse])
async def update_item(item_id: str, data: ItemLicitacionUpdate):
    return await ItemLicitacionUpdateService.process(item_id, data)
