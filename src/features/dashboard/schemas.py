from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class KPIs(BaseModel):
    licitaciones_cargadas: int
    licitaciones_en_proceso: int
    licitaciones_adjudicadas: int
    presupuesto_total: float
    monto_adjudicado_total: float

class MetricasFinancieras(BaseModel):
    monto_postulado: float
    monto_adjudicado: float
    monto_perdido: float
    monto_en_evaluacion: float
    win_rate: float

class DashboardResponse(BaseModel):
    kpis: KPIs
    distribucion_estados: Dict[str, int]
    metricas_financieras: MetricasFinancieras
    por_usuario: Dict[str, Dict[str, Any]]
    uso_mensual: Dict[str, int]
    items_mas_cotizados: List[List[Any]] # e.g. [["Guantes", 20], ...]
    items_mas_adjudicados: List[List[Any]]
    licitaciones: List[Dict[str, Any]]
