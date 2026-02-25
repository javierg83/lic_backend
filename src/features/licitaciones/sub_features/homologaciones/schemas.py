from uuid import UUID
from pydantic import BaseModel
from typing import List, Optional

class ProductoHomologado(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    stock_disponible: Optional[int] = None
    ubicacion_stock: Optional[str] = None

class CandidatoHomologacion(BaseModel):
    ranking: int
    producto: ProductoHomologado
    score_similitud: Optional[float] = None
    razonamiento: Optional[str] = None

class ResultadoHomologacion(BaseModel):
    homologacion_id: str
    item_key: str
    nombre_item: str
    cantidad: Optional[int] = None
    descripcion_detectada: Optional[str] = None
    candidatos: List[CandidatoHomologacion]

class HomologacionesResponse(BaseModel):
    homologaciones: List[ResultadoHomologacion]
