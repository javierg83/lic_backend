from pydantic import BaseModel
from typing import Optional

class ItemLicitacionUpdate(BaseModel):
    nombre_item: Optional[str] = None
    cantidad: Optional[float] = None
    unidad: Optional[str] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None

class ItemLicitacionUpdateResponse(BaseModel):
    id: str
    nombre_item: str
    cantidad: float
    unidad: str
    descripcion: str
    observaciones: str
