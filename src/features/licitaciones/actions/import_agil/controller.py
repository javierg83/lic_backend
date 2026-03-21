from fastapi import APIRouter
from src.core.responses import ApiResponse
from .schemas import ImportCompraAgilRequest, ImportCompraAgilResponse
from .service import CompraAgilService

router = APIRouter()

@router.post("/import-agil", response_model=ApiResponse[ImportCompraAgilResponse])
async def import_compra_agil(request: ImportCompraAgilRequest):
    return await CompraAgilService.import_compra_agil(request.url_or_code)
