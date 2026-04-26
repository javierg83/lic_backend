from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nombre: str
    rut: str
    activo: bool = True

class ClienteCreate(ClienteBase):
    admin_username: Optional[str] = None
    admin_password: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: str
    created_at: Optional[datetime] = None
    umbral: float = 60.0

    model_config = ConfigDict(from_attributes=True)

class ClienteDetailResponse(ClienteResponse):
    palabras_clave: List[str] = []
    admin_username: Optional[str] = None
    alerta_homologacion_activa: bool = True
    correo_contacto: Optional[str] = None
