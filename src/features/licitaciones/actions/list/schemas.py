from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class LicitacionListItem(BaseModel):
    id: UUID
    nombre: Optional[str] = None
    estado: str
    fecha_carga: datetime

class LicitacionListResponse(BaseModel):
    licitaciones: List[LicitacionListItem]
