from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class DatosEconomicosUpdate(BaseModel):
    presupuesto_referencial: Optional[Decimal] = None
    moneda: Optional[str] = None
    forma_pago: Optional[str] = None
    plazo_pago: Optional[str] = None
    fuente_financiamiento: Optional[str] = None
    observaciones: Optional[str] = None

class DatosEconomicosUpdateResponse(BaseModel):
    id: str
    licitacion_id: str
    presupuesto_referencial: Optional[Decimal] = None
    moneda: Optional[str] = None
    forma_pago: Optional[str] = None
    plazo_pago: Optional[str] = None
    fuente_financiamiento: Optional[str] = None
    observaciones: Optional[str] = None
