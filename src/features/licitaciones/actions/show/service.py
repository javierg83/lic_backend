from uuid import UUID
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import LicitacionShowResponse, ArchivoShow

class LicitacionShowService:
    @staticmethod
    async def process(licitacion_id: UUID) -> ApiResponse[LicitacionShowResponse]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Fetch Licitacion Basic Info
                    cur.execute(
                        """
                        SELECT id, codigo_licitacion, nombre, entidad_solicitante, unidad_compra, descripcion, estado, fecha_carga, id_interno, estado_publicacion, tipo_licitacion
                        FROM licitaciones 
                        WHERE id = %s
                        """,
                        (str(licitacion_id),)
                    )
                    row = cur.fetchone()
                    
                    if not row:
                        return ApiResponse.fail(
                            message="Licitación no encontrada",
                            status_code=404
                        )
                    
                    # Fetch Files
                    cur.execute(
                        """
                        SELECT id, id_interno, nombre_archivo_org, tipo_contenido, peso_bytes, estado_procesamiento, fecha_subida
                        FROM licitacion_archivos
                        WHERE licitacion_id = %s AND obsoleto = FALSE
                        ORDER BY fecha_subida ASC
                        """,
                        (str(licitacion_id),)
                    )
                    file_rows = cur.fetchall()
                    archivos = [
                        ArchivoShow(
                            id=frow[0],
                            id_interno=frow[1],
                            nombre_archivo_org=frow[2],
                            tipo_contenido=frow[3],
                            peso_bytes=frow[4],
                            estado_procesamiento=frow[5],
                            fecha_subida=frow[6]
                        ) for frow in file_rows
                    ]

                    licitacion = LicitacionShowResponse(
                        id=row[0],
                        codigo=row[1],
                        titulo=row[2],
                        organismo=row[3],
                        unidad_solicitante=row[4],
                        descripcion=row[5],
                        estado=row[6],
                        fecha_carga=row[7],
                        id_interno=row[8],
                        estado_publicacion=row[9],
                        tipo_licitacion=row[10],
                        archivos=archivos
                    )
            
            return ApiResponse.ok(
                data=licitacion,
                message="Licitación obtenida exitosamente"
            )

        except Exception as e:
            print(f"ERROR LicitacionShowService: {str(e)}")
            import traceback
            traceback.print_exc()
            return ApiResponse.fail(
                message="No se pudo cargar la información de la licitación seleccionada.",
                error=str(e)
            )
        finally:
            conn.close()
