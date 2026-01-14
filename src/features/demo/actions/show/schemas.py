from pydantic import BaseModel
from datetime import date

class DemoShowIn(BaseModel):
    licitacion_id: int

class DemoShowOut(BaseModel):
    licitacion_nombre: str
    licitacion_encargado: str
    licitacion_fecha_inicio: date
    licitacion_fecha_termino: date
    licitacion_fecha_creacion: date
