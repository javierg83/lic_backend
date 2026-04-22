from fastapi import APIRouter, Depends
from uuid import UUID
from .service import LicitacionShowService
from .schemas import LicitacionShowResponse
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required

router = APIRouter()

@router.get("/{licitacion_id}", response_model=ApiResponse[LicitacionShowResponse])
async def show_licitacion(licitacion_id: UUID, user_data: dict = Depends(auth_required)):
    cliente_id = user_data.get("cliente_id")
    rol = user_data.get("rol")
    return await LicitacionShowService.process(licitacion_id, cliente_id=cliente_id, rol=rol)
