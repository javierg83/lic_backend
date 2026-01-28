from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import ItemLicitacionUpdate, ItemLicitacionUpdateResponse

class ItemLicitacionUpdateService:
    @staticmethod
    async def process(item_id: str, data: ItemLicitacionUpdate) -> ApiResponse[ItemLicitacionUpdateResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Build update query dynamically based on provided fields
                    fields_to_update = []
                    params = []
                    
                    update_data = data.model_dump(exclude_unset=True)
                    if not update_data:
                         return ApiResponse.fail(message="No se proporcionaron datos para actualizar")
                    
                    for key, value in update_data.items():
                        fields_to_update.append(f"{key} = %s")
                        params.append(value)
                    
                    params.append(item_id)
                    query = f"UPDATE items_licitacion SET {', '.join(fields_to_update)} WHERE id = %s RETURNING id, nombre_item, cantidad, unidad, descripcion, observaciones"
                    
                    cur.execute(query, tuple(params))
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(message="Ítem no encontrado")
                    
                    updated_item = ItemLicitacionUpdateResponse(
                        id=row['id'],
                        nombre_item=row['nombre_item'],
                        cantidad=row['cantidad'],
                        unidad=row['unidad'],
                        descripcion=row['descripcion'],
                        observaciones=row['observaciones']
                    )
                    
                    return ApiResponse.ok(
                        data=updated_item,
                        message="Ítem actualizado exitosamente"
                    )
        except Exception as e:
            print(f"ERROR ItemLicitacionUpdateService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo actualizar el ítem. Por favor, reintente más tarde.",
                error=str(e)
            )
        finally:
            conn.close()
