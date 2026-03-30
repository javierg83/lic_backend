from uuid import UUID
from datetime import date
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import GestionUpdateRequest
from ..show.schemas import GestionShowResponse

class GestionUpdateService:
    @staticmethod
    async def process(licitacion_id: UUID, data: GestionUpdateRequest) -> ApiResponse[GestionShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    fecha_resultado = data.fecha_resultado
                    fecha_cierre = data.fecha_cierre

                    if data.estado in ['ADJUDICADA', 'NO_ADJUDICADA'] and fecha_resultado is None:
                        fecha_resultado = date.today()
                    
                    if data.estado == 'CERRADA' and fecha_cierre is None:
                        fecha_cierre = date.today()

                    # Validar estado actual sistémico
                    cur.execute("SELECT estado FROM licitaciones WHERE id = %s", (str(licitacion_id),))
                    row_lic = cur.fetchone()
                    if not row_lic:
                        return ApiResponse.fail(message="Licitación no encontrada", status_code=404)
                    estado_actual = row_lic['estado']
                    
                    estados_sistemicos_bloqueados = [
                        "PENDIENTE", "PROCESANDO_DOCUMENTOS", "DOCUMENTOS_PROCESADOS", 
                        "ERROR_PROCESO_DOCUMENTAL", "REQUIERE_REVISION_TECNICA", 
                        "EXTRACCION_SEMANTICA_EN_PROCESO", "EXTRACCION_SEMANTICA_COMPLETADA", 
                        "HOMOLOGACION_EN_PROCESO", "ERROR_EXTRACCION_SEMANTICA"
                    ]
                    if estado_actual in estados_sistemicos_bloqueados:
                        return ApiResponse.fail(
                            message="La licitación no puede avanzar a gestión sin haber finalizado su procesamiento previo.",
                            status_code=400
                        )

                    # Actualizar estado maestro
                    cur.execute("UPDATE licitaciones SET estado = %s WHERE id = %s", (data.estado, str(licitacion_id)))

                    cur.execute(
                        """
                        INSERT INTO gestion_licitaciones (
                            licitacion_id, estado, monto, observaciones, fecha_resultado, fecha_cierre, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, timezone('utc'::text, now())
                        )
                        ON CONFLICT (licitacion_id) DO UPDATE SET
                            estado = EXCLUDED.estado,
                            monto = EXCLUDED.monto,
                            observaciones = EXCLUDED.observaciones,
                            fecha_resultado = EXCLUDED.fecha_resultado,
                            fecha_cierre = EXCLUDED.fecha_cierre,
                            updated_at = timezone('utc'::text, now())
                        RETURNING id, licitacion_id, estado, monto, observaciones, fecha_resultado, fecha_cierre, created_at, updated_at
                        """,
                        (
                            str(licitacion_id),
                            data.estado,
                            data.monto,
                            data.observaciones,
                            fecha_resultado,
                            fecha_cierre
                        )
                    )
                    row = cur.fetchone()
                    
                    datos = GestionShowResponse(
                        id=row['id'],
                        licitacion_id=row['licitacion_id'],
                        estado=row['estado'],
                        monto=float(row['monto']) if row['monto'] is not None else None,
                        observaciones=row['observaciones'],
                        fecha_resultado=row['fecha_resultado'],
                        fecha_cierre=row['fecha_cierre'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
            
            return ApiResponse.ok(
                data=datos,
                message="Gestión de licitación actualizada exitosamente"
            )

        except Exception as e:
            print(f"ERROR GestionUpdateService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo actualizar la gestión de la licitación.",
                error=str(e)
            )
        finally:
            conn.close()
