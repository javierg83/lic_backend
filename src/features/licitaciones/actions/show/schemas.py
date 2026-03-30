from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ArchivoShow(BaseModel):
    id: UUID
    id_interno: int
    nombre_archivo_org: str
    tipo_contenido: Optional[str] = None
    peso_bytes: Optional[int] = None
    estado_procesamiento: str
    fecha_subida: datetime

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
    tipo_licitacion: Optional[str] = None
    fecha_carga: datetime
    archivos: List[ArchivoShow] = []
