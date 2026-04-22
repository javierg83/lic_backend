import json
from src.core.database import Database

class DashboardService:
    @staticmethod
    def get_resumen(cliente_id: str = None) -> dict:
        # Filtro tenant: si hay cliente_id, solo sus licitaciones; si es admin (None), todas
        tenant_filter = "AND lc.cliente_id = %(cliente_id)s" if cliente_id else ""
        params = {"cliente_id": cliente_id} if cliente_id else {}

        # ── KPIs ─────────────────────────────────────────────────────────────
        kpis_result = {"licitaciones_cargadas": 0, "licitaciones_en_proceso": 0,
                       "licitaciones_adjudicadas": 0, "presupuesto_total": 0}
        try:
            kpis_query = f"""
                SELECT 
                    (SELECT COUNT(*) FROM licitaciones_descargadas ld
                     JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = ld.id
                     WHERE 1=1 {tenant_filter}) as licitaciones_cargadas,
                    (SELECT COUNT(*) FROM licitaciones_descargadas ld
                     JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = ld.id
                     WHERE ld.estado NOT IN ('ADJUDICADA', 'NO_ADJUDICADA', 'DECLINADA', 'CERRADA') {tenant_filter}) as licitaciones_en_proceso,
                    (SELECT COUNT(*) FROM licitaciones_descargadas ld
                     JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = ld.id
                     WHERE ld.estado = 'ADJUDICADA' {tenant_filter}) as licitaciones_adjudicadas,
                    (SELECT COALESCE(SUM(fl.presupuesto_referencial), 0)
                     FROM finanzas_licitacion fl
                     JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = fl.licitacion_id
                     WHERE 1=1 {tenant_filter}) as presupuesto_total
            """
            row = Database.execute_query(kpis_query, params=params, fetch_all=False)
            if row:
                kpis_result = dict(row)
        except Exception as e:
            print(f"[Dashboard] KPIs error: {e}")

        # ── Monto adjudicado (requiere gestion_licitaciones) ─────────────────
        monto_adjudicado_total = 0
        try:
            monto_adj_query = f"""
                SELECT COALESCE(SUM(g.monto), 0) as monto_adjudicado_total
                FROM gestion_licitaciones g
                JOIN licitaciones_descargadas l ON g.licitacion_id = l.id
                JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = l.id
                WHERE l.estado = 'ADJUDICADA' {tenant_filter}
            """
            row = Database.execute_query(monto_adj_query, params=params, fetch_all=False)
            if row:
                monto_adjudicado_total = row["monto_adjudicado_total"] or 0
        except Exception as e:
            print(f"[Dashboard] Monto adjudicado error (tabla puede no existir): {e}")

        # ── Listado de licitaciones ───────────────────────────────────────────
        licitaciones_result = []
        try:
            licitaciones_query = f"""
                SELECT 
                    l.id,
                    l.codigo_licitacion,
                    COALESCE(lc.estado_interno, l.estado, 'Sin Asignar') as estado,
                    COALESCE(l.nombre, 'Sin Asignar') as usuario,
                    l.fecha_carga,
                    l.fecha_cierre as fecha_limite,
                    COALESCE((SELECT SUM(fl.presupuesto_referencial) FROM finanzas_licitacion fl WHERE fl.licitacion_id = l.id), 0) as presupuesto_maximo,
                    0 as monto_adjudicado,
                    (SELECT COUNT(*) FROM items_licitacion il WHERE il.licitacion_id = l.id) as cantidad_items_total,
                    0 as cantidad_items_adjudicados
                FROM licitaciones_descargadas l
                JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = l.id
                WHERE 1=1 {tenant_filter}
            """
            licitaciones_result = Database.execute_query(licitaciones_query, params=params) or []
        except Exception as e:
            print(f"[Dashboard] Licitaciones error: {e}")

        # ── Rendimiento por usuario ────────────────────────────────────────────
        por_usuario = {}
        for r in licitaciones_result:
            u = r["usuario"] if isinstance(r, dict) else r[3]
            if u not in por_usuario:
                por_usuario[u] = {"cargadas": 0, "adjudicadas": 0, "monto_adjudicado": 0,
                                  "total_items": 0, "items_adjudicados": 0}
            estado = r["estado"] if isinstance(r, dict) else r[2]
            por_usuario[u]["cargadas"] += 1
            if estado == 'ADJUDICADA':
                por_usuario[u]["adjudicadas"] += 1
        for u, stats in por_usuario.items():
            stats["porcentaje_licitaciones"] = round((stats["adjudicadas"] / stats["cargadas"]) * 100, 1) if stats["cargadas"] > 0 else 0
            stats["porcentaje_items"] = 0

        # ── Uso mensual ───────────────────────────────────────────────────────
        uso_mensual = {}
        try:
            uso_query = f"""
                SELECT TO_CHAR(l.fecha_carga, 'YYYY-MM') as mes, COUNT(*) as cantidad
                FROM licitaciones_descargadas l
                JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = l.id
                WHERE l.fecha_carga IS NOT NULL {tenant_filter}
                GROUP BY TO_CHAR(l.fecha_carga, 'YYYY-MM')
                ORDER BY mes ASC
            """
            uso_result = Database.execute_query(uso_query, params=params) or []
            uso_mensual = {row["mes"]: row["cantidad"] for row in uso_result}
        except Exception as e:
            print(f"[Dashboard] Uso mensual error: {e}")

        # ── Items más cotizados ────────────────────────────────────────────────
        items_mas_cotizados = []
        try:
            cotizados_query = """
                SELECT nombre_item, COUNT(*) as freq
                FROM items_licitacion
                WHERE nombre_item IS NOT NULL AND nombre_item <> ''
                GROUP BY nombre_item
                ORDER BY freq DESC
                LIMIT 10
            """
            cotizados_result = Database.execute_query(cotizados_query) or []
            items_mas_cotizados = [[r["nombre_item"], r["freq"]] for r in cotizados_result]
        except Exception as e:
            print(f"[Dashboard] Items cotizados error: {e}")

        # ── Items más adjudicados ──────────────────────────────────────────────
        items_mas_adjudicados = []
        try:
            adjudicados_query = """
                SELECT nombre_item, COUNT(*) as freq
                FROM items_licitacion
                WHERE adjudicado = true AND nombre_item IS NOT NULL AND nombre_item <> ''
                GROUP BY nombre_item
                ORDER BY freq DESC
                LIMIT 10
            """
            adjudicados_result = Database.execute_query(adjudicados_query) or []
            items_mas_adjudicados = [[r["nombre_item"], r["freq"]] for r in adjudicados_result]
        except Exception as e:
            print(f"[Dashboard] Items adjudicados error: {e}")

        # ── Distribución de estados ────────────────────────────────────────────
        distribucion_estados = {}
        try:
            estados_query = f"""
                SELECT COALESCE(l.estado, 'PENDIENTE') as estado, COUNT(*) as cantidad
                FROM licitaciones_descargadas l
                JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = l.id
                WHERE 1=1 {tenant_filter}
                GROUP BY COALESCE(l.estado, 'PENDIENTE')
            """
            estados_result = Database.execute_query(estados_query, params=params) or []
            distribucion_estados = {row["estado"]: row["cantidad"] for row in estados_result}
        except Exception as e:
            print(f"[Dashboard] Estados error: {e}")

        # ── Métricas financieras ───────────────────────────────────────────────
        metricas_financieras = {
            "monto_postulado": 0.0, "monto_adjudicado": 0.0,
            "monto_perdido": 0.0, "monto_en_evaluacion": 0.0, "win_rate": 0.0
        }
        try:
            finanzas_query = f"""
                SELECT l.estado, SUM(g.monto) as total_monto
                FROM gestion_licitaciones g
                JOIN licitaciones_descargadas l ON g.licitacion_id = l.id
                JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = l.id
                WHERE g.monto IS NOT NULL {tenant_filter}
                GROUP BY l.estado
            """
            finanzas_result = Database.execute_query(finanzas_query, params=params) or []
            mp = ma = mpe = mev = 0.0
            for row in finanzas_result:
                est, val = row["estado"], float(row["total_monto"] or 0)
                if est in ['POSTULACION_ENVIADA', 'OFERTA_PRESENTADA', 'EN_EVALUACION', 'ADJUDICADA', 'NO_ADJUDICADA']:
                    mp += val
                if est == 'ADJUDICADA': ma += val
                if est == 'NO_ADJUDICADA': mpe += val
                if est in ['POSTULACION_ENVIADA', 'OFERTA_PRESENTADA', 'EN_EVALUACION']: mev += val
            metricas_financieras = {
                "monto_postulado": mp, "monto_adjudicado": ma,
                "monto_perdido": mpe, "monto_en_evaluacion": mev,
                "win_rate": round((ma / mp) * 100, 1) if mp > 0 else 0.0
            }
        except Exception as e:
            print(f"[Dashboard] Finanzas error (tabla puede no existir): {e}")

        # ── Format licitaciones output ─────────────────────────────────────────
        for r in licitaciones_result:
            if isinstance(r, dict):
                r["id"] = str(r["id"]) if r.get("id") else ""
                r["fecha_carga"] = r["fecha_carga"].isoformat() if r.get("fecha_carga") else None
                r["fecha_limite"] = r["fecha_limite"].isoformat() if r.get("fecha_limite") else None
                r["presupuesto_maximo"] = float(r.get("presupuesto_maximo") or 0)
                r["monto_adjudicado"] = float(r.get("monto_adjudicado") or 0)

        return {
            "kpis": {
                "licitaciones_cargadas": kpis_result.get("licitaciones_cargadas") or 0,
                "licitaciones_en_proceso": kpis_result.get("licitaciones_en_proceso") or 0,
                "licitaciones_adjudicadas": kpis_result.get("licitaciones_adjudicadas") or 0,
                "presupuesto_total": float(kpis_result.get("presupuesto_total") or 0),
                "monto_adjudicado_total": float(monto_adjudicado_total or 0)
            },
            "distribucion_estados": distribucion_estados,
            "metricas_financieras": metricas_financieras,
            "por_usuario": por_usuario,
            "uso_mensual": uso_mensual,
            "items_mas_cotizados": items_mas_cotizados,
            "items_mas_adjudicados": items_mas_adjudicados,
            "licitaciones": licitaciones_result
        }
