from fastapi import APIRouter, Depends
from uuid import UUID
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .schemas import HomologacionesResponse, GuardarHomologacionRequest
from .service import HomologacionesService, HomologacionesSaveService

router = APIRouter()

@router.get("/{id}/homologaciones", response_model=ApiResponse[HomologacionesResponse])
async def get_homologaciones_by_licitacion(id: UUID, user_data: dict = Depends(auth_required)):
    cliente_id = user_data.get("cliente_id")
    return await HomologacionesService.process(id, cliente_id=cliente_id)

@router.post("/{id}/homologaciones/guardar", response_model=ApiResponse[None])
async def save_homologaciones(id: UUID, req: GuardarHomologacionRequest, user_data: dict = Depends(auth_required)):
    cliente_id = user_data.get("cliente_id")
    return await HomologacionesSaveService.process(id, req, cliente_id=cliente_id)
