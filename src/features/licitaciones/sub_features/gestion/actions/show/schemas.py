from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class GestionShowResponse(BaseModel):
    id: Optional[UUID] = None
    licitacion_id: UUID
    estado: str
    monto: Optional[float] = None
    observaciones: Optional[str] = None
    fecha_resultado: Optional[date] = None
    fecha_cierre: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
