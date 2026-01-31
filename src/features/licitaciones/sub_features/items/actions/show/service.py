from uuid import UUID, uuid4
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import ItemsLicitacionListResponse, ItemLicitacionResponse

class ItemsLicitacionShowService:
    @staticmethod
    async def process(licitacion_id: str) -> ApiResponse[ItemsLicitacionListResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if items exist
                    cur.execute(
                        "SELECT id, licitacion_id, item_key, nombre_item, cantidad, unidad, descripcion, observaciones FROM items_licitacion WHERE licitacion_id = %s",
                        (licitacion_id,)
                    )
                    rows = cur.fetchall()
                    
                    if not rows:
                        rows = []
                    
                    items = [
                        ItemLicitacionResponse(
                            id=row['id'],
                            licitacion_id=row['licitacion_id'],
                            item_key=row['item_key'],
                            nombre_item=row['nombre_item'],
                            cantidad=row['cantidad'],
                            unidad=row['unidad'],
                            descripcion=row['descripcion'],
                            observaciones=row['observaciones']
                        ) for row in rows
                    ]
            
            return ApiResponse.ok(
                data=ItemsLicitacionListResponse(items=items),
                message="Ítems obtenidos exitosamente"
            )

        except Exception as e:
            print(f"ERROR ItemsLicitacionShowService: {str(e)}")
            return ApiResponse.fail(
                message="No se pudieron cargar los ítems. Por favor, reintente más tarde.",
                error=str(e)
            )
        finally:
            conn.close()
