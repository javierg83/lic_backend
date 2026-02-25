from fastapi import APIRouter, HTTPException
from uuid import UUID

from . import schemas
from . import service

router = APIRouter()

@router.get(
    "/{licitacion_id}/auditoria",
    response_model=schemas.AuditoriaListResponse,
    summary="Obtiene la auditoría de extracciones semánticas de una licitación"
)
def get_auditoria_licitacion(licitacion_id: UUID):
    try:
        registros = service.get_auditoria(licitacion_id)
        return schemas.AuditoriaListResponse(data=registros)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
