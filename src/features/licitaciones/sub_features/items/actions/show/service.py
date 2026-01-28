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
                        # SEEDING logic
                        items_to_insert = []
                        # Example data based on the provided image
                        mock_data = [
                            ("Bomba centrífuga", 1, "Global", "Bomba centrífuga con potencia mínima de 1 HP, 0.75 kw, con capacidad de caudal de 22 m. de altura mínima."),
                            ("Estanque vertical", 1, "Global", "Estanque vertical 10.000L para almacenamiento de agua potable con densidad igual o menor a 1,0 kg/L, el diseño puede ser cilíndrico, con manto ondulado."),
                            ("Kit de instalación", 1, "Global", "Kit de instalación incluye sensor de nivel 3 m, controlador de presión hasta 2 HP, salida 1\" PVC, válvula de corte 1\"."),
                        ]
                        
                        for i in range(1, 16):
                            # Use mock data if available, otherwise generic
                            if i <= len(mock_data):
                                nombre, cant, unid, desc = mock_data[i-1]
                            else:
                                nombre = f"Producto / Servicio {i}"
                                cant = i
                                unid = "Unidad"
                                desc = f"Descripción detallada del producto o servicio número {i}"
                                
                            items_to_insert.append((
                                str(uuid4()),
                                licitacion_id,
                                str(uuid4()), # semantic_run_id
                                f"ITEM-{i:03d}",
                                nombre,
                                cant,
                                unid,
                                desc,
                                "Generado automáticamente"
                            ))
                        
                        cur.executemany(
                            """
                            INSERT INTO items_licitacion (id, licitacion_id, semantic_run_id, item_key, nombre_item, cantidad, unidad, descripcion, observaciones)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            items_to_insert
                        )
                        
                        # Fetch again
                        cur.execute(
                            "SELECT id, licitacion_id, item_key, nombre_item, cantidad, unidad, descripcion, observaciones FROM items_licitacion WHERE licitacion_id = %s",
                            (licitacion_id,)
                        )
                        rows = cur.fetchall()
                    
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
