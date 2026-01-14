from pydantic import BaseModel
from datetime import date

class DemoListIn(BaseModel):
    pass  # Request vacío

class DemoListOut(BaseModel):
    id: int
    nombre: str
    valor: float
    fecha: date
