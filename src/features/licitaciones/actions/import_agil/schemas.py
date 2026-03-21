import json
from typing import Optional, List
from pydantic import BaseModel

class ImportCompraAgilRequest(BaseModel):
    url_or_code: str

class ArchivoCompraAgilResponse(BaseModel):
    nombre: str
    ruta: str
    uuid: str

class ImportCompraAgilResponse(BaseModel):
    codigo: str
    licitacion_id: Optional[str] = None
    mensaje: str
    archivos_descargados: List[ArchivoCompraAgilResponse]
