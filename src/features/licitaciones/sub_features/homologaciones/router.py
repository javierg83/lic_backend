from fastapi import APIRouter
from uuid import UUID
from src.core.responses import ApiResponse
from .schemas import HomologacionesResponse
from .service import HomologacionesService

router = APIRouter()

@router.get("/{id}/homologaciones", response_model=ApiResponse[HomologacionesResponse])
async def get_homologaciones_by_licitacion(id: UUID):
    return await HomologacionesService.process(id)
