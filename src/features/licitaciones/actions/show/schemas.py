from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class LicitacionShowResponse(BaseModel):
    id: UUID
    id_interno: Optional[int] = None
    codigo: Optional[str] = None
    titulo: Optional[str] = None
    organismo: Optional[str] = None
    unidad_solicitante: Optional[str] = None
    descripcion: Optional[str] = None
    estado_publicacion: Optional[str] = None
    estado: Optional[str] = None
    fecha_carga: datetime
