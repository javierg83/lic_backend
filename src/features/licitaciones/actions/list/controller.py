from fastapi import APIRouter, Depends
from .service import LicitacionListService
from .schemas import LicitacionListResponse
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required

router = APIRouter()

@router.get("/list", response_model=ApiResponse[LicitacionListResponse])
async def list_licitaciones(user_data: dict = Depends(auth_required)):
    cliente_id = user_data.get("cliente_id")
    rol = user_data.get("rol")
    return await LicitacionListService.process(cliente_id=cliente_id, rol=rol)
