from fastapi import APIRouter
from uuid import UUID
from src.core.responses import ApiResponse
from .schemas import HomologacionesResponse, GuardarHomologacionRequest
from .service import HomologacionesService, HomologacionesSaveService

router = APIRouter()

@router.get("/{id}/homologaciones", response_model=ApiResponse[HomologacionesResponse])
async def get_homologaciones_by_licitacion(id: UUID):
    return await HomologacionesService.process(id)

@router.post("/{id}/homologaciones/guardar", response_model=ApiResponse[None])
async def save_homologaciones(id: UUID, req: GuardarHomologacionRequest):
    return await HomologacionesSaveService.process(id, req)
