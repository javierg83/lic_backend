from uuid import UUID
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import GestionShowResponse

class GestionShowService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[GestionShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT g.id, l.id as licitacion_id, l.estado, g.monto, g.observaciones, g.fecha_resultado, g.fecha_cierre, g.created_at, g.updated_at
                        FROM licitaciones l
                        LEFT JOIN gestion_licitaciones g ON l.id = g.licitacion_id
                        WHERE l.id = %s
                        """,
                        (str(licitacion_id),)
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(
                            message="Licitación no encontrada",
                            status_code=404
                        )
                    
                    datos = GestionShowResponse(
                        id=row['id'] if row['id'] else None,
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
                message="Gestión de licitación obtenida exitosamente"
            )

        except Exception as e:
            print(f"ERROR GestionShowService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo cargar la gestión de la licitación.",
                error=str(e)
            )
        finally:
            conn.close()
