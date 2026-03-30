from fastapi import APIRouter
from uuid import UUID
from src.core.responses import ApiResponse
from .service import GestionShowService
from .schemas import GestionShowResponse

router = APIRouter()

@router.get("/{id}/gestion", response_model=ApiResponse[GestionShowResponse])
async def get_gestion(id: UUID):
    return await GestionShowService.process(id)
