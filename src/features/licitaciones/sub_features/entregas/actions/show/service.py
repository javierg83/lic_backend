from uuid import UUID
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import EntregaShowResponse

class EntregaShowService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[EntregaShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 
                            licitacion_id, 
                            direccion_entrega, 
                            comuna_entrega, 
                            plazo_entrega, 
                            fecha_entrega,
                            contacto_entrega,
                            horario_entrega,
                            instrucciones_entrega
                        FROM licitacion_entregas 
                        WHERE licitacion_id = %s
                        """,
                        (str(licitacion_id),)
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        # Si no existe, devolvemos un objeto vacío en lugar de un error
                        return ApiResponse.ok(
                            data=EntregaShowResponse(licitacion_id=licitacion_id),
                            message="No hay detalles de entrega registrados."
                        )
                    
                    data = EntregaShowResponse(
                        licitacion_id=row[0],
                        direccion_entrega=row[1],
                        comuna_entrega=row[2],
                        plazo_entrega=row[3],
                        fecha_entrega=row[4],
                        contacto_entrega=row[5],
                        horario_entrega=row[6],
                        instrucciones_entrega=row[7]
                    )
            
            return ApiResponse.ok(
                data=data,
                message="Detalles de entrega obtenidos exitosamente"
            )

        except Exception as e:
            print(f"ERROR EntregaShowService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo cargar la información de entrega.",
                error=str(e)
            )
        finally:
            conn.close()
