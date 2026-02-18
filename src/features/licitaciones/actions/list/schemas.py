from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class LicitacionListItem(BaseModel):
    id: UUID
    id_interno: Optional[int] = None
    nombre: Optional[str] = None
    estado: Optional[str] = None
    fecha_carga: datetime

class LicitacionListResponse(BaseModel):
    licitaciones: List[LicitacionListItem]
