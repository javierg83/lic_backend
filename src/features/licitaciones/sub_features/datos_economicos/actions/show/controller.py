from fastapi import APIRouter, Depends
from uuid import UUID
from src.core.responses import ApiResponse
from .service import DatosEconomicosShowService
from .schemas import DatosEconomicosShowResponse

router = APIRouter()

@router.get("/{id}/datos-economicos", response_model=ApiResponse[DatosEconomicosShowResponse])
async def get_datos_economicos(id: UUID):
    return await DatosEconomicosShowService.process(id)
