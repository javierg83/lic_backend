from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ClienteBase(BaseModel):
    nombre: str
    rut: str
    activo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ClienteDetailResponse(ClienteResponse):
    palabras_clave: List[str] = []
