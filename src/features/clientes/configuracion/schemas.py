from pydantic import BaseModel
from typing import Optional

class ClienteConfiguracionResponse(BaseModel):
    cliente_id: str
    alerta_homologacion_umbral: float = 60.0
    alerta_homologacion_activa: bool = True
    correo_contacto: Optional[str] = None

class ClienteConfiguracionUpdate(BaseModel):
    alerta_homologacion_umbral: Optional[float] = None
    alerta_homologacion_activa: Optional[bool] = None
    correo_contacto: Optional[str] = None
