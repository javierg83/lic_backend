from uuid import UUID
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import LicitacionShowResponse

class LicitacionShowService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[LicitacionShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, codigo_licitacion, nombre, organismo_solicitante, NULL as unidad_solicitante, descripcion, estado, fecha_carga, id_interno
                        FROM licitaciones 
                        WHERE id = %s
                        """,
                        (str(licitacion_id),)
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(
                            message="Licitación no encontrada",
                            status_code=404
                        )
                    
                    licitacion = LicitacionShowResponse(
                        id=row[0],
                        codigo=row[1],
                        titulo=row[2],
                        organismo=row[3],
                        unidad_solicitante=row[4],
                        descripcion=row[5],
                        estado=row[6],
                        fecha_carga=row[7],
                        id_interno=row[8]
                    )
            
            return ApiResponse.ok(
                data=licitacion,
                message="Licitación obtenida exitosamente"
            )

        except Exception as e:
            print(f"ERROR LicitacionShowService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo cargar la información de la licitación seleccionada.",
                error=str(e)
            )
        finally:
            conn.close()
