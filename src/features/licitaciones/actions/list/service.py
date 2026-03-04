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
                        SELECT 
                            l.id, 
                            l.nombre, 
                            l.estado, 
                            l.fecha_carga, 
                            l.id_interno, 
                            l.estado_publicacion,
                            f.presupuesto_referencial,
                            f.moneda,
                            (SELECT COUNT(id) FROM items_licitacion il WHERE il.licitacion_id = l.id) as cantidad_items,
                            (SELECT COUNT(DISTINCT hp.item_key) FROM homologaciones_productos hp WHERE hp.licitacion_id = l.id AND hp.candidato_seleccionado_id IS NOT NULL) as cantidad_homologados
                        FROM licitaciones l
                        LEFT JOIN finanzas_licitacion f ON l.id = f.licitacion_id
                        ORDER BY l.fecha_carga DESC
                        """
                    )
                    rows = cur.fetchall()
                    
                    licitaciones = []
                    for row in rows:
                        cantidad_items = row[8] or 0
                        cantidad_homologados = row[9] or 0
                        porcentaje_homologacion = round((cantidad_homologados / cantidad_items) * 100, 2) if cantidad_items > 0 else 0.0
                        
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
                            porcentaje_homologacion=porcentaje_homologacion
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
