import json
from src.core.database import Database

class DashboardService:
    @staticmethod
    def get_resumen() -> dict:
        # KPIs
        kpis_query = """
            SELECT 
                (SELECT COUNT(*) FROM licitaciones WHERE obsoleto = false) as licitaciones_cargadas,
                (SELECT COUNT(*) FROM licitaciones WHERE obsoleto = false AND estado NOT IN ('ADJUDICADA', 'NO_ADJUDICADA', 'DECLINADA', 'CERRADA')) as licitaciones_en_proceso,
                (SELECT COUNT(*) FROM licitaciones WHERE obsoleto = false AND estado = 'ADJUDICADA') as licitaciones_adjudicadas,
                (SELECT COALESCE(SUM(presupuesto_referencial), 0) FROM finanzas_licitacion WHERE obsoleto = false) as presupuesto_total
        """
        kpis_result = Database.execute_query(kpis_query, fetch_all=False)
        if not kpis_result:
             kpis_result = {
                 "licitaciones_cargadas": 0, "licitaciones_en_proceso": 0,
                 "licitaciones_adjudicadas": 0, "presupuesto_total": 0
             }

        monto_adj_query = """
            SELECT COALESCE(SUM(g.monto), 0) as monto_adjudicado_total
            FROM gestion_licitaciones g
            JOIN licitaciones l ON g.licitacion_id = l.id
            WHERE l.obsoleto = false AND l.estado = 'ADJUDICADA'
        """
        monto_adj_result = Database.execute_query(monto_adj_query, fetch_all=False)
        monto_adjudicado_total = monto_adj_result["monto_adjudicado_total"] if monto_adj_result else 0

        # Licitaciones Detail
        licitaciones_query = """
            SELECT 
                l.id,
                l.codigo_licitacion,
                COALESCE(l.estado, 'Sin Asignar') as estado,
                COALESCE(l.usuario, 'Sin Asignar') as usuario,
                l.fecha_carga,
                l.fecha_cierre as fecha_limite,
                COALESCE((SELECT SUM(presupuesto_referencial) FROM finanzas_licitacion WHERE licitacion_id = l.id AND obsoleto = false), 0) as presupuesto_maximo,
                COALESCE((SELECT monto FROM gestion_licitaciones WHERE licitacion_id = l.id LIMIT 1), 0) as monto_adjudicado,
                (SELECT COUNT(*) FROM items_licitacion WHERE licitacion_id = l.id AND obsoleto = false) as cantidad_items_total,
                (SELECT COUNT(*) FROM items_licitacion WHERE licitacion_id = l.id AND adjudicado = true AND obsoleto = false) as cantidad_items_adjudicados
            FROM licitaciones l
            WHERE l.obsoleto = false
        """
        licitaciones_result = Database.execute_query(licitaciones_query)

        # Rendimiento por usuario
        por_usuario = {}
        for row in licitaciones_result:
             u = row["usuario"]
             if u not in por_usuario:
                  por_usuario[u] = {
                       "cargadas": 0, "adjudicadas": 0, "monto_adjudicado": 0,
                       "total_items": 0, "items_adjudicados": 0
                  }
             por_usuario[u]["cargadas"] += 1
             if row["estado"] == 'ADJUDICADA':
                  por_usuario[u]["adjudicadas"] += 1
                  por_usuario[u]["monto_adjudicado"] += (row["monto_adjudicado"] or 0)
             
             por_usuario[u]["total_items"] += row["cantidad_items_total"]
             por_usuario[u]["items_adjudicados"] += row["cantidad_items_adjudicados"]
        
        for u, stats in por_usuario.items():
             stats["porcentaje_licitaciones"] = round((stats["adjudicadas"] / stats["cargadas"]) * 100, 1) if stats["cargadas"] > 0 else 0
             stats["porcentaje_items"] = round((stats["items_adjudicados"] / stats["total_items"]) * 100, 1) if stats["total_items"] > 0 else 0

        # Uso mensual
        uso_query = """
            SELECT TO_CHAR(fecha_carga, 'YYYY-MM') as mes, COUNT(*) as cantidad
            FROM licitaciones
            WHERE obsoleto = false AND fecha_carga IS NOT NULL
            GROUP BY TO_CHAR(fecha_carga, 'YYYY-MM')
            ORDER BY mes ASC
        """
        uso_result = Database.execute_query(uso_query)
        uso_mensual = {row["mes"]: row["cantidad"] for row in uso_result} if uso_result else {}

        # Items mas cotizados
        cotizados_query = """
            SELECT nombre_item, COUNT(*) as freq
            FROM items_licitacion
            WHERE obsoleto = false AND nombre_item IS NOT NULL AND nombre_item <> ''
            GROUP BY nombre_item
            ORDER BY freq DESC
            LIMIT 10
        """
        cotizados_result = Database.execute_query(cotizados_query)
        items_mas_cotizados = [[r["nombre_item"], r["freq"]] for r in cotizados_result] if cotizados_result else []

        # Items mas adjudicados
        adjudicados_query = """
            SELECT nombre_item, COUNT(*) as freq
            FROM items_licitacion
            WHERE obsoleto = false AND adjudicado = true AND nombre_item IS NOT NULL AND nombre_item <> ''
            GROUP BY nombre_item
            ORDER BY freq DESC
            LIMIT 10
        """
        adjudicados_result = Database.execute_query(adjudicados_query)
        items_mas_adjudicados = [[r["nombre_item"], r["freq"]] for r in adjudicados_result] if adjudicados_result else []

        # Format Final Licitaciones output (string dates and ids)
        for r in licitaciones_result:
             r["id"] = str(r["id"]) if r.get("id") else ""
             r["fecha_carga"] = r["fecha_carga"].isoformat() if r.get("fecha_carga") else None
             r["fecha_limite"] = r["fecha_limite"].isoformat() if r.get("fecha_limite") else None
             r["presupuesto_maximo"] = float(r["presupuesto_maximo"] or 0)
             r["monto_adjudicado"] = float(r["monto_adjudicado"] or 0)

        estados_query = """
            SELECT COALESCE(estado, 'PENDIENTE') as estado, COUNT(*) as cantidad
            FROM licitaciones
            WHERE obsoleto = false
            GROUP BY COALESCE(estado, 'PENDIENTE')
        """
        estados_result = Database.execute_query(estados_query)
        distribucion_estados = {row["estado"]: row["cantidad"] for row in estados_result} if estados_result else {}

        finanzas_query = """
            SELECT 
                l.estado,
                SUM(g.monto) as total_monto
            FROM gestion_licitaciones g
            JOIN licitaciones l ON g.licitacion_id = l.id
            WHERE l.obsoleto = false AND g.monto IS NOT NULL
            GROUP BY l.estado
        """
        finanzas_result = Database.execute_query(finanzas_query)
        
        monto_postulado = 0.0
        monto_adjudicado = 0.0
        monto_perdido = 0.0
        monto_en_evaluacion = 0.0

        if finanzas_result:
            for row in finanzas_result:
                est = row["estado"]
                val = float(row["total_monto"] or 0)
                if est in ['POSTULACION_ENVIADA', 'OFERTA_PRESENTADA', 'EN_EVALUACION', 'ADJUDICADA', 'NO_ADJUDICADA']:
                    monto_postulado += val
                if est == 'ADJUDICADA':
                    monto_adjudicado += val
                if est == 'NO_ADJUDICADA':
                    monto_perdido += val
                if est in ['POSTULACION_ENVIADA', 'OFERTA_PRESENTADA', 'EN_EVALUACION']:
                    monto_en_evaluacion += val

        win_rate = round((monto_adjudicado / monto_postulado) * 100, 1) if monto_postulado > 0 else 0.0

        metricas_financieras = {
            "monto_postulado": monto_postulado,
            "monto_adjudicado": monto_adjudicado,
            "monto_perdido": monto_perdido,
            "monto_en_evaluacion": monto_en_evaluacion,
            "win_rate": win_rate
        }

        return {
             "kpis": {
                  "licitaciones_cargadas": kpis_result["licitaciones_cargadas"] or 0,
                  "licitaciones_en_proceso": kpis_result["licitaciones_en_proceso"] or 0,
                  "licitaciones_adjudicadas": kpis_result["licitaciones_adjudicadas"] or 0,
                  "presupuesto_total": float(kpis_result["presupuesto_total"] or 0),
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
