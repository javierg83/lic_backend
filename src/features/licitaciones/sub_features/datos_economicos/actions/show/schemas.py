from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from uuid import UUID

class DatosEconomicosShowResponse(BaseModel):
    id: UUID
    licitacion_id: UUID
    presupuesto_referencial: Optional[Decimal] = None
    moneda: Optional[str] = None
    forma_pago: Optional[str] = None
    plazo_pago: Optional[str] = None
    fuente_financiamiento: Optional[str] = None
    observaciones: Optional[str] = None
