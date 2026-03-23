from pydantic import BaseModel
from typing import Optional

class EntregaUpdate(BaseModel):
    direccion_entrega: Optional[str] = None
    comuna_entrega: Optional[str] = None
    plazo_entrega: Optional[str] = None
    fecha_entrega: Optional[str] = None
    contacto_entrega: Optional[str] = None
    horario_entrega: Optional[str] = None
    instrucciones_entrega: Optional[str] = None
