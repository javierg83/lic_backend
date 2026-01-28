from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

class ItemLicitacionBase(BaseModel):
    item_key: Optional[str] = None
    nombre_item: Optional[str] = None
    cantidad: Optional[Decimal] = None
    unidad: Optional[str] = None
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None

class ItemLicitacionResponse(ItemLicitacionBase):
    id: UUID
    licitacion_id: str

class ItemsLicitacionListResponse(BaseModel):
    items: List[ItemLicitacionResponse]
