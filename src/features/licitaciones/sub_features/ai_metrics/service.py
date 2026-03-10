from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import AITokenUsageCreate, AITokenUsageResponse, AIMetricsSummary, AIMetricsResponse
import uuid

class AIMetricsService:
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
                        
                    res = AITokenUsageResponse(
                        id=row[0],
                        licitacion_id=str(row[1]),
                        action=row[2],
                        provider=row[3],
                        model=row[4],
                        input_tokens=row[5],
                        output_tokens=row[6],
                        total_tokens=row[7],
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
                        logs.append(AITokenUsageResponse(
                            id=r[0],
                            licitacion_id=str(r[1]),
                            action=r[2],
                            provider=r[3],
                            model=r[4],
                            input_tokens=r[5],
                            output_tokens=r[6],
                            total_tokens=r[7],
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
                    
                    for sr in summary_rows:
                        total_in += sr[3] or 0
                        total_out += sr[4] or 0
                        total_all += sr[5] or 0
                        summary.append(AIMetricsSummary(
                            action=sr[0],
                            provider=sr[1],
                            model=sr[2],
                            total_input=sr[3] or 0,
                            total_output=sr[4] or 0,
                            total_tokens=sr[5] or 0
                        ))
                        
                    metrics = AIMetricsResponse(
                        licitacion_id=licitacion_id,
                        logs=logs,
                        summary=summary,
                        total_input_all=total_in,
                        total_output_all=total_out,
                        total_all=total_all
                    )
                    
            return ApiResponse.ok(data=metrics, message="Métricas de IA obtenidas")
        except Exception as e:
            print(f"ERROR AIMetricsService get_metrics: {str(e)}")
            return ApiResponse.fail(message="No se pudieron obtener las métricas", error=str(e))
        finally:
            conn.close()
