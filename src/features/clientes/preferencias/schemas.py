from pydantic import BaseModel
from typing import List

class ClientePreferenciasBase(BaseModel):
    palabras_clave: List[str]

class ClientePreferenciasUpdate(ClientePreferenciasBase):
    pass

class ClientePreferenciasResponse(ClientePreferenciasBase):
    cliente_id: str
