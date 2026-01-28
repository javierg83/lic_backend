from fastapi import APIRouter
from .service import DatosEconomicosUpdateService
from .schemas import DatosEconomicosUpdate, DatosEconomicosUpdateResponse
from src.core.responses import ApiResponse
from uuid import UUID

router = APIRouter()

@router.put("/{licitacion_id}/datos-economicos", response_model=ApiResponse[DatosEconomicosUpdateResponse])
async def update_datos_economicos(licitacion_id: UUID, data: DatosEconomicosUpdate):
    return await DatosEconomicosUpdateService.process(str(licitacion_id), data)
