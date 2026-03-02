from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class KPIs(BaseModel):
    licitaciones_cargadas: int
    licitaciones_en_proceso: int
    licitaciones_adjudicadas: int
    presupuesto_total: float
    monto_adjudicado_total: float

class DashboardResponse(BaseModel):
    kpis: KPIs
    por_usuario: Dict[str, Dict[str, Any]]
    uso_mensual: Dict[str, int]
    items_mas_cotizados: List[List[Any]] # e.g. [["Guantes", 20], ...]
    items_mas_adjudicados: List[List[Any]]
    licitaciones: List[Dict[str, Any]]
