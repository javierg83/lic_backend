from uuid import UUID
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import EntregaUpdate
from ..show.schemas import EntregaShowResponse

class EntregaUpdateService:
    @staticmethod
    async def process(licitacion_id: UUID, data: EntregaUpdate) -> ApiResponse[EntregaShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # UPSERT handling logic (Insert or Update)
                    cur.execute(
                        """
                        INSERT INTO licitacion_entregas (
                            licitacion_id, 
                            direccion_entrega, 
                            comuna_entrega, 
                            plazo_entrega, 
                            fecha_entrega,
                            contacto_entrega,
                            horario_entrega,
                            instrucciones_entrega
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (licitacion_id) DO UPDATE SET
                            direccion_entrega = EXCLUDED.direccion_entrega,
                            comuna_entrega = EXCLUDED.comuna_entrega,
                            plazo_entrega = EXCLUDED.plazo_entrega,
                            fecha_entrega = EXCLUDED.fecha_entrega,
                            contacto_entrega = EXCLUDED.contacto_entrega,
                            horario_entrega = EXCLUDED.horario_entrega,
                            instrucciones_entrega = EXCLUDED.instrucciones_entrega,
                            actualizado_en = CURRENT_TIMESTAMP
                        RETURNING licitacion_id, direccion_entrega, comuna_entrega, plazo_entrega, fecha_entrega, contacto_entrega, horario_entrega, instrucciones_entrega
                        """,
                        (
                            str(licitacion_id),
                            data.direccion_entrega,
                            data.comuna_entrega,
                            data.plazo_entrega,
                            data.fecha_entrega,
                            data.contacto_entrega,
                            data.horario_entrega,
                            data.instrucciones_entrega
                        )
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(message="No se pudo actualizar o insertar los datos de entrega.")

                    result_data = EntregaShowResponse(
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
                data=result_data,
                message="Detalles de entrega guardados exitosamente"
            )

        except Exception as e:
            print(f"ERROR EntregaUpdateService: {str(e)}")
            return ApiResponse.fail(
                message="Error al intentar grabar la información de entrega.",
                error=str(e)
            )
        finally:
            conn.close()
