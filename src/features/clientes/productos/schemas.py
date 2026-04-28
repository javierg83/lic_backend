from pydantic import BaseModel
from typing import List, Optional

class ProductoCSVRow(BaseModel):
    codigo: Optional[str] = None
    nombre_producto: str
    descripcion: Optional[str] = None
    precio_referencial: Optional[float] = None

class UploadProductosResponse(BaseModel):
    total_procesados: int
    total_insertados: int
    errores: List[str]

class ProductoResponse(BaseModel):
    id: str
    codigo: Optional[str] = None
    nombre_producto: str
    descripcion: Optional[str] = None
    precio_referencial: Optional[float] = None
