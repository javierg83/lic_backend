from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LicitacionUpdate(BaseModel):
    codigo: Optional[str] = None
    titulo: Optional[str] = None
    organismo: Optional[str] = None
    unidad_solicitante: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None

class LicitacionUpdateResponse(BaseModel):
    id: UUID
    codigo: Optional[str] = None
    titulo: Optional[str] = None
    organismo: Optional[str] = None
    unidad_solicitante: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = None
