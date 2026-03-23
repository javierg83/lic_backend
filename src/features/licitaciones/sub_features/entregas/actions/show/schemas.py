from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class EntregaShowResponse(BaseModel):
    licitacion_id: UUID
    direccion_entrega: Optional[str] = None
    comuna_entrega: Optional[str] = None
    plazo_entrega: Optional[str] = None
    fecha_entrega: Optional[str] = None
    contacto_entrega: Optional[str] = None
    horario_entrega: Optional[str] = None
    instrucciones_entrega: Optional[str] = None
