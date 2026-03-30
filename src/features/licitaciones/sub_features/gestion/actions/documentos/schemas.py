from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class GestionDocumentoRequest(BaseModel):
    tipo_documento: str
    nombre_archivo: str
    ruta_archivo: str
    usuario: Optional[str] = None
    observacion: Optional[str] = None

class GestionDocumentoResponse(BaseModel):
    id: UUID
    gestion_id: UUID
    tipo_documento: str
    nombre_archivo: str
    ruta_archivo: str
    fecha_subida: datetime
    usuario: Optional[str] = None
    observacion: Optional[str] = None
