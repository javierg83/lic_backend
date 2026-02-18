from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class FileValidationResult(BaseModel):
    nombre: str
    valido: bool
    error: Optional[str] = None

class LicitacionNewResponse(BaseModel):
    id: Optional[UUID] = None
    id_interno: Optional[int] = None
    nombre: str
    archivos_procesados: List[FileValidationResult]
