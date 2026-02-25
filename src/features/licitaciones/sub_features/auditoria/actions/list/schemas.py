from pydantic import BaseModel, Field
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class FuenteAuditoria(BaseModel):
    documento: Optional[str] = None
    pagina: Optional[int] = None
    parrafo: Optional[str] = None
    redis_key: Optional[str] = None

class AuditoriaItem(BaseModel):
    id: UUID
    licitacion_id: UUID
    semantic_run_id: Optional[UUID] = None
    concepto: str
    campo_extraido: str
    valor_extraido: Optional[str] = None
    razonamiento: Optional[str] = None
    lista_fuentes: Optional[List[FuenteAuditoria]] = None
    creado_en: datetime

    class Config:
        from_attributes = True

class AuditoriaListResponse(BaseModel):
    data: List[AuditoriaItem]
