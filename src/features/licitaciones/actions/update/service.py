from uuid import UUID
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import LicitacionUpdate, LicitacionUpdateResponse

class LicitacionUpdateService:
    @staticmethod
    async def process(licitacion_id: UUID, data: LicitacionUpdate) -> ApiResponse[LicitacionUpdateResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if licitacion exists
                    cur.execute("SELECT id FROM licitaciones_descargadas WHERE id = %s", (str(licitacion_id),))
                    if not cur.fetchone():
                        return ApiResponse.fail(message="Licitación no encontrada", status_code=404)
                    
                    # Build update query
                    fields_to_update = []
                    params = []
                    
                    # Map frontend fields to DB fields
                    mapping = {
                        "codigo": "codigo_licitacion",
                        "titulo": "nombre",
                        "organismo": "organismo_solicitante",
                        "descripcion": "descripcion",
                        "estado": "estado"
                    }
                    
                    update_data = data.model_dump(exclude_unset=True)
                    if not update_data:
                        return ApiResponse.fail(message="No se proporcionaron datos para actualizar")
                    
                    for key, value in update_data.items():
                        if key in mapping:
                            fields_to_update.append(f"{mapping[key]} = %s")
                            params.append(value)
                    
                    if not fields_to_update:
                        return ApiResponse.fail(message="No hay campos válidos para actualizar")

                    params.append(str(licitacion_id))
                    
                    query = f"""
                        UPDATE licitaciones_descargadas 
                        SET {', '.join(fields_to_update)} 
                        WHERE id = %s 
                        RETURNING id, codigo_licitacion as codigo, nombre as titulo, organismo_solicitante as organismo, descripcion, estado
                    """
                    
                    cur.execute(query, tuple(params))
                    updated_row = cur.fetchone()
                    
                    if not updated_row:
                         return ApiResponse.fail(message="Error al actualizar la licitación")

                    response_data = LicitacionUpdateResponse(
                        id=updated_row['id'],
                        codigo=updated_row['codigo'],
                        titulo=updated_row['titulo'],
                        organismo=updated_row['organismo'],
                        unidad_solicitante=None, # Not in DB yet
                        descripcion=updated_row['descripcion'],
                        estado=updated_row['estado']
                    )
                    
                    return ApiResponse.ok(
                        data=response_data,
                        message="Licitación actualizada exitosamente"
                    )
        except Exception as e:
            print(f"ERROR LicitacionUpdateService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudieron guardar los cambios de la licitación.",
                error=str(e)
            )
        finally:
            conn.close()
