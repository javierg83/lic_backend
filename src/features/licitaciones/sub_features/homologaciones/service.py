from uuid import UUID
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import HomologacionesResponse, ResultadoHomologacion, CandidatoHomologacion, ProductoHomologado, GuardarHomologacionRequest

class HomologacionesService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[HomologacionesResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT
                            hp.id AS homologacion_id,
                            hp.candidato_seleccionado_id,
                            hp.item_key,
                            hp.descripcion_detectada,
                            il.nombre_item,
                            il.cantidad,
                            ch.ranking,
                            ch.producto_codigo,
                            ch.producto_nombre,
                            ch.producto_descripcion,
                            ch.stock_disponible,
                            ch.ubicacion_stock,
                            ch.score_similitud,
                            ch.razonamiento
                        FROM homologaciones_productos hp
                        LEFT JOIN items_licitacion il
                            ON il.licitacion_id::text = hp.licitacion_id::text
                            AND (
                                LOWER(TRIM(il.item_key)) = LOWER(TRIM(hp.item_key))
                                OR LOWER(TRIM(il.nombre_item)) = LOWER(TRIM(hp.item_key))
                            )
                        LEFT JOIN candidatos_homologacion ch
                            ON ch.homologacion_id = hp.id
                        WHERE hp.licitacion_id = %s
                        ORDER BY hp.fecha_homologacion DESC, hp.item_key, ch.ranking
                        """,
                        (str(licitacion_id),)
                    )
                    rows = cur.fetchall()

            print(f"DEBUG [Homologaciones] Licitación ID consultado: {licitacion_id}")
            print(f"DEBUG [Homologaciones] Filas retornadas por SQL: {len(rows)}")
            for i, r in enumerate(rows):
                print(f"DEBUG -> Fila {i}: item_key='{r.get('item_key')}' | candidato='{r.get('producto_nombre')}' | rank='{r.get('ranking')}'")

            items_dict = {}

            for r in rows:
                homologacion_id = str(r["homologacion_id"])
                item_key = str(r["item_key"])
                nombre_item = str(r["nombre_item"] or item_key)

                if homologacion_id not in items_dict:
                    items_dict[homologacion_id] = ResultadoHomologacion(
                        homologacion_id=homologacion_id,
                        item_key=item_key,
                        nombre_item=nombre_item,
                        cantidad=r["cantidad"],
                        descripcion_detectada=r["descripcion_detectada"],
                        candidato_seleccionado_id=str(r["candidato_seleccionado_id"]) if r["candidato_seleccionado_id"] else None,
                        candidatos=[]
                    )

                if r["ranking"] is not None:
                    candidato = CandidatoHomologacion(
                        ranking=r["ranking"],
                        producto=ProductoHomologado(
                            codigo=str(r["producto_codigo"]),
                            nombre=str(r["producto_nombre"]),
                            descripcion=r["producto_descripcion"],
                            stock_disponible=r["stock_disponible"],
                            ubicacion_stock=r["ubicacion_stock"]
                        ),
                        score_similitud=float(r["score_similitud"]) if r["score_similitud"] is not None else None,
                        razonamiento=r["razonamiento"]
                    )
                    items_dict[homologacion_id].candidatos.append(candidato)

            return ApiResponse.ok(
                data=HomologacionesResponse(homologaciones=list(items_dict.values())),
                message="Homologaciones obtenidas exitosamente." if len(items_dict) > 0 else "No se encontraron ítems homologados."
            )

        except Exception as e:
            print(f"ERROR HomologacionesService: {str(e)}")
            return ApiResponse.fail(
                message="Error interno al consultar las homologaciones.",
                error=str(e)
            )
        finally:
            conn.close()

class HomologacionesSaveService:
    @staticmethod
    async def process(licitacion_id: UUID, req: GuardarHomologacionRequest) -> ApiResponse[None]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    for homologacion_id_str, candidato_codigo in req.selecciones.items():
                        if candidato_codigo:
                            # Buscar primero el UUID del candidato usando el codigo de producto
                            cur.execute(
                                """
                                SELECT id FROM candidatos_homologacion 
                                WHERE homologacion_id = %s AND producto_codigo = %s
                                LIMIT 1
                                """,
                                (homologacion_id_str, candidato_codigo)
                            )
                            row = cur.fetchone()
                            if row:
                                candidato_id = row[0]
                                cur.execute(
                                    "UPDATE homologaciones_productos SET candidato_seleccionado_id = %s WHERE id = %s",
                                    (candidato_id, homologacion_id_str)
                                )
                        else:
                            # Caso desmarcar o null
                            cur.execute(
                                "UPDATE homologaciones_productos SET candidato_seleccionado_id = NULL WHERE id = %s",
                                (homologacion_id_str,)
                            )
            return ApiResponse.ok(message="Selecciones guardadas correctamente", data=None)

        except Exception as e:
            print(f"ERROR HomologacionesSaveService: {str(e)}")
            return ApiResponse.fail(
                message="Error interno al guardar las homologaciones.",
                error=str(e)
            )
        finally:
            conn.close()
