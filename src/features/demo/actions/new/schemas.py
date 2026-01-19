from pydantic import BaseModel
from datetime import date

class DemoNewIn(BaseModel):
    nombre: str
    telefono: str
    fecha_nacimiento: date
    edad: int

class DemoNewOut(BaseModel):
    id: int
    nombre: str
    success: bool
