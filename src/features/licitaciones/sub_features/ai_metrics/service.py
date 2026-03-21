from src.core.database import Database
from src.core.responses import ApiResponse
from src.core.config import AI_MODEL_PRICES, USD_TO_CLP
from .schemas import AITokenUsageCreate, AITokenUsageResponse, AIMetricsSummary, AIMetricsResponse
import uuid

class AIMetricsService:
    @staticmethod
    def _calculate_cost(model: str, input_tokens: int, output_tokens: int):
        prices = AI_MODEL_PRICES.get(model, AI_MODEL_PRICES.get("gpt-4o-mini")) # Fallback to mini if unknown
        
        input_cost = (input_tokens / 1_000_000) * prices.get("input", 0)
        output_cost = (output_tokens / 1_000_000) * prices.get("output", 0)
        
        total_usd = input_cost + output_cost
        total_clp = total_usd * USD_TO_CLP
        
        return input_cost, output_cost, total_usd, total_clp

    @staticmethod
    async def create_log(licitacion_id: str, data: AITokenUsageCreate) -> ApiResponse[AITokenUsageResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO ai_token_usage_logs (
                            licitacion_id, action, provider, model, input_tokens, output_tokens
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id, licitacion_id, action, provider, model, input_tokens, output_tokens, total_tokens, created_at
                    """
                    
                    cur.execute(query, (
                        licitacion_id,
                        data.action,
                        data.provider,
                        data.model,
                        data.input_tokens,
                        data.output_tokens
                    ))
                    
                    row = cur.fetchone()
                    if not row:
                        raise Exception("No se insertó el registro de tokens")
                    
                    in_cost, out_cost, total_cost, total_clp = AIMetricsService._calculate_cost(row[4], row[5], row[6])
                        
                    res = AITokenUsageResponse(
                        id=row[0],
                        licitacion_id=str(row[1]),
                        action=row[2],
                        provider=row[3],
                        model=row[4],
                        input_tokens=row[5],
                        output_tokens=row[6],
                        total_tokens=row[7],
                        input_cost=in_cost,
                        output_cost=out_cost,
                        total_cost=total_cost,
                        total_cost_clp=total_clp,
                        created_at=row[8]
                    )
                    
            return ApiResponse.ok(data=res, message="Registro creado exitosamente")
        except Exception as e:
            print(f"ERROR AIMetricsService create_log: {str(e)}")
            return ApiResponse.fail(message="No se pudo registrar el uso de tokens", error=str(e))
        finally:
            conn.close()

    @staticmethod
    async def get_metrics(licitacion_id: str) -> ApiResponse[AIMetricsResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # 1. Obtener logs individuales
                    cur.execute("""
                        SELECT id, licitacion_id, action, provider, model, input_tokens, output_tokens, total_tokens, created_at
                        FROM ai_token_usage_logs
                        WHERE licitacion_id = %s
                        ORDER BY created_at DESC
                    """, (licitacion_id,))
                    
                    rows = cur.fetchall()
                    logs = []
                    for r in rows:
                        in_cost, out_cost, total_cost, total_clp = AIMetricsService._calculate_cost(r[4], r[5], r[6])
                        logs.append(AITokenUsageResponse(
                            id=r[0],
                            licitacion_id=str(r[1]),
                            action=r[2],
                            provider=r[3],
                            model=r[4],
                            input_tokens=r[5],
                            output_tokens=r[6],
                            total_tokens=r[7],
                            input_cost=in_cost,
                            output_cost=out_cost,
                            total_cost=total_cost,
                            total_cost_clp=total_clp,
                            created_at=r[8]
                        ))
                    
                    # 2. Obtener resumen agrupado
                    cur.execute("""
                        SELECT action, provider, model, SUM(input_tokens), SUM(output_tokens), SUM(total_tokens)
                        FROM ai_token_usage_logs
                        WHERE licitacion_id = %s
                        GROUP BY action, provider, model
                        ORDER BY action
                    """, (licitacion_id,))
                    
                    summary_rows = cur.fetchall()
                    summary = []
                    total_in = 0
                    total_out = 0
                    total_all = 0
                    total_usd_all = 0.0
                    total_clp_all = 0.0
                    
                    for sr in summary_rows:
                        t_in = sr[3] or 0
                        t_out = sr[4] or 0
                        t_tokens = sr[5] or 0
                        
                        in_cost, out_cost, total_usd, total_clp = AIMetricsService._calculate_cost(sr[2], t_in, t_out)
                        
                        total_in += t_in
                        total_out += t_out
                        total_all += t_tokens
                        total_usd_all += total_usd
                        total_clp_all += total_clp
                        
                        summary.append(AIMetricsSummary(
                            action=sr[0],
                            provider=sr[1],
                            model=sr[2],
                            total_input=t_in,
                            total_output=t_out,
                            total_tokens=t_tokens,
                            input_cost=in_cost,
                            output_cost=out_cost,
                            total_cost=total_usd,
                            total_cost_clp=total_clp
                        ))
                        
                    metrics = AIMetricsResponse(
                        licitacion_id=licitacion_id,
                        logs=logs,
                        summary=summary,
                        total_input_all=total_in,
                        total_output_all=total_out,
                        total_all=total_all,
                        total_cost_all=total_usd_all,
                        total_cost_all_clp=total_clp_all
                    )
                    
            return ApiResponse.ok(data=metrics, message="Métricas de IA obtenidas")
        except Exception as e:
            print(f"ERROR AIMetricsService get_metrics: {str(e)}")
            return ApiResponse.fail(message="No se pudieron obtener las métricas", error=str(e))
        finally:
            conn.close()
