from pydantic import BaseModel
from typing import Optional
from datetime import date

class GestionUpdateRequest(BaseModel):
    estado: str
    monto: Optional[float] = None
    observaciones: Optional[str] = None
    fecha_resultado: Optional[date] = None
    fecha_cierre: Optional[date] = None
