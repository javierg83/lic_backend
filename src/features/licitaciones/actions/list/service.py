from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import LicitacionListResponse, LicitacionListItem

class LicitacionListService:
    @staticmethod
    async def process() -> ApiResponse[LicitacionListResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT id, nombre, estado, fecha_carga 
                        FROM licitaciones 
                        ORDER BY fecha_carga DESC
                        """
                    )
                    rows = cur.fetchall()
                    
                    licitaciones = [
                        LicitacionListItem(
                            id=row[0],
                            nombre=row[1],
                            estado=row[2],
                            fecha_carga=row[3]
                        ) for row in rows
                    ]
            
            return ApiResponse.ok(
                data=LicitacionListResponse(licitaciones=licitaciones),
                message="Licitaciones obtenidas exitosamente"
            )

        except Exception as e:
            print(f"ERROR LicitacionListService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo obtener el listado de licitaciones. Por favor, reintente más tarde.",
                error=str(e)
            )
        finally:
            conn.close()
