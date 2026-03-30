from fastapi import APIRouter
from uuid import UUID
from src.core.responses import ApiResponse
from .service import GestionUpdateService
from .schemas import GestionUpdateRequest
from ..show.schemas import GestionShowResponse

router = APIRouter()

@router.post("/{id}/gestion", response_model=ApiResponse[GestionShowResponse])
async def update_gestion(id: UUID, data: GestionUpdateRequest):
    return await GestionUpdateService.process(id, data)
