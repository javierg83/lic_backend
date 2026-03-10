from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class LicitacionListItem(BaseModel):
    id: UUID
    id_interno: Optional[int] = None
    nombre: Optional[str] = None
    estado: Optional[str] = None
    estado_publicacion: Optional[str] = None
    presupuesto: Optional[float] = None
    moneda: Optional[str] = None
    fecha_carga: datetime
    cantidad_items: Optional[int] = 0
    cantidad_homologados: Optional[int] = 0
    porcentaje_homologacion: Optional[float] = 0.0
    tipo_licitacion: Optional[str] = None

class LicitacionListResponse(BaseModel):
    licitaciones: List[LicitacionListItem]
