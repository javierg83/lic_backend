from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import LicitacionListResponse, LicitacionListItem

class LicitacionListService:
    @staticmethod
    async def process(cliente_id: str = None, rol: str = None) -> ApiResponse[LicitacionListResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Admin ve TODAS las licitaciones, sin importar si tiene cliente_id o no
                    if rol == "admin":
                        cur.execute(
                            """
                            SELECT 
                                ld.id, 
                                ld.nombre, 
                                COALESCE(lc.estado_interno, ld.estado) as estado,
                                ld.fecha_carga, 
                                ld.id_interno, 
                                ld.estado_publicacion,
                                NULL::numeric as presupuesto_referencial,
                                NULL::text as moneda,
                                (SELECT COUNT(id) FROM items_licitacion il WHERE il.licitacion_id = ld.id) as cantidad_items,
                                0 as cantidad_homologados,
                                ld.tipo_licitacion,
                                0 as cantidad_con_candidatos,
                                60.0 as umbral_cliente
                            FROM licitaciones_descargadas ld
                            LEFT JOIN licitaciones_clientes lc ON lc.licitacion_descargada_id = ld.id
                            ORDER BY ld.fecha_carga DESC
                            """
                        )
                    else:
                        # Usuario cliente: solo ve su bandeja
                        cur.execute(
                            """
                            SELECT 
                                ld.id, 
                                ld.nombre, 
                                lc.estado_interno as estado, 
                                ld.fecha_carga, 
                                ld.id_interno, 
                                ld.estado_publicacion,
                                f.presupuesto_referencial,
                                f.moneda,
                                (SELECT COUNT(id) FROM items_licitacion il WHERE il.licitacion_id = ld.id) as cantidad_items,
                                (SELECT COUNT(DISTINCT hp.item_key) 
                                 FROM homologaciones_productos hp 
                                 WHERE hp.licitacion_cliente_id = lc.id 
                                   AND hp.candidato_seleccionado_id IS NOT NULL) as cantidad_homologados,
                                ld.tipo_licitacion,
                                (SELECT COUNT(DISTINCT hp.item_key) 
                                 FROM homologaciones_productos hp 
                                 JOIN candidatos_homologacion ch ON ch.homologacion_id = hp.id
                                 WHERE hp.licitacion_cliente_id = lc.id) as cantidad_con_candidatos,
                                COALESCE(cc.alerta_homologacion_umbral, 60.0) as umbral_cliente
                            FROM licitaciones_clientes lc
                            JOIN licitaciones_descargadas ld ON lc.licitacion_descargada_id = ld.id
                            LEFT JOIN finanzas_licitacion f ON ld.id = f.licitacion_id
                            LEFT JOIN cliente_configuracion cc ON cc.cliente_id = lc.cliente_id
                            WHERE lc.cliente_id = %s
                            ORDER BY ld.fecha_carga DESC
                            """,
                            (cliente_id,)
                        )
                    
                    rows = cur.fetchall()
                    
                    licitaciones = []
                    for row in rows:
                        cantidad_items = row[8] or 0
                        cantidad_homologados = row[9] or 0
                        cantidad_con_candidatos = row[11] or 0
                        umbral_cliente = float(row[12]) if row[12] is not None else 60.0
                        
                        porcentaje_homologacion = round((cantidad_homologados / cantidad_items) * 100, 2) if cantidad_items > 0 else 0.0
                        porcentaje_cobertura = round((cantidad_con_candidatos / cantidad_items) * 100, 2) if cantidad_items > 0 else 0.0
                        alerta_homologacion = porcentaje_cobertura >= umbral_cliente
                        
                        licitaciones.append(LicitacionListItem(
                            id=row[0],
                            nombre=row[1],
                            estado=row[2],
                            fecha_carga=row[3],
                            id_interno=row[4],
                            estado_publicacion=row[5],
                            presupuesto=float(row[6]) if row[6] is not None else None,
                            moneda=row[7],
                            cantidad_items=cantidad_items,
                            cantidad_homologados=cantidad_homologados,
                            porcentaje_homologacion=porcentaje_homologacion,
                            tipo_licitacion=row[10],
                            cantidad_con_candidatos=cantidad_con_candidatos,
                            porcentaje_cobertura=porcentaje_cobertura,
                            alerta_homologacion=alerta_homologacion,
                            umbral_homologacion=umbral_cliente
                        ))
            
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
