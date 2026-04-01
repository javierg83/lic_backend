import os
import redis
from typing import List, Optional
from psycopg2.extras import RealDictCursor
from src.core.database import Database
from src.core.responses import ApiResponse
from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, REDIS_DB

class DeleteLicitacionService:
    @staticmethod
    def delete_licitacion(licitacion_id: str) -> ApiResponse:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "licitaciones")

        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 1. Verificar si existe la licitación
                    cur.execute("SELECT id FROM licitaciones WHERE id = %s", (licitacion_id,))
                    if not cur.fetchone():
                        return ApiResponse.fail(message="Licitación no encontrada", status_code=404)

                    # 2. Borrar en Storage (archivos de gestion)
                    cur.execute("SELECT ruta_archivo FROM gestion_licitacion_documentos WHERE gestion_id = %s", (licitacion_id,))
                    rutas_documentos = [row['ruta_archivo'] for row in cur.fetchall() if row['ruta_archivo'] and not row['ruta_archivo'].startswith('http')]
                    
                    if rutas_documentos and supabase_url and supabase_key:
                        from supabase import create_client, Client
                        supabase: Client = create_client(supabase_url, supabase_key)
                        try:
                            supabase.storage.from_(supabase_bucket).remove(rutas_documentos)
                            print(f"🗑️ Archivos eliminados de Supabase Storage: {len(rutas_documentos)}")
                        except Exception as storage_err:
                            print(f"⚠️ Error al eliminar de Storage (continuando): {storage_err}")

                    # 3. Borrar en Redis
                    try:
                        cur.execute(
                            "SELECT redis_key FROM semantic_evidences WHERE semantic_run_id IN (SELECT id FROM semantic_runs WHERE licitacion_id = %s)", 
                            (licitacion_id,)
                        )
                        redis_keys = [row['redis_key'] for row in cur.fetchall() if row['redis_key']]
                        
                        r = redis.Redis(
                            host=REDIS_HOST,
                            port=int(REDIS_PORT),
                            username=REDIS_USERNAME,
                            password=REDIS_PASSWORD,
                            db=int(REDIS_DB),
                            decode_responses=True
                        )
                        r.ping() # Validar conexion
                        
                        if redis_keys:
                            r.delete(*redis_keys)
                            print(f"🗑️ Llaves semánticas eliminadas de Redis: {len(redis_keys)}")

                        # Borrado de temporales usando SCAN
                        contador_temporales = 0
                        for key in r.scan_iter(f"*{licitacion_id}*"):
                            r.delete(key)
                            contador_temporales += 1
                            
                        if contador_temporales > 0:
                            print(f"🗑️ Llaves temporales eliminadas de Redis: {contador_temporales}")

                    except Exception as redis_err:
                         print(f"⚠️ Error al eliminar de Redis (continuando): {redis_err}")
                         # Important: We must not continue if the transaction is aborted
                         if "transaction is aborted" in str(redis_err):
                            raise redis_err

                    # 4. Borrar de la BD (Postgres). Borrado manual preventivo por si no hay CASCADE.
                    # Use savepoints to avoid aborting the main transaction if a table doesn't exist
                    try:
                        cur.execute("SAVEPOINT pre_delete")
                        
                        # Limpiar evidencias y resultados
                        cur.execute("DELETE FROM semantic_evidences WHERE semantic_run_id IN (SELECT id FROM semantic_runs WHERE licitacion_id = %s)", (licitacion_id,))
                        cur.execute("DELETE FROM semantic_results WHERE semantic_run_id IN (SELECT id FROM semantic_runs WHERE licitacion_id = %s)", (licitacion_id,))
                        cur.execute("DELETE FROM semantic_runs WHERE licitacion_id = %s", (licitacion_id,))
                        
                        # Limpiar documentos de gestion
                        cur.execute("DELETE FROM gestion_licitacion_documentos WHERE gestion_id = %s", (licitacion_id,))
                        
                        # Limpiar archivos base
                        cur.execute("DELETE FROM licitacion_archivos WHERE licitacion_id = %s", (licitacion_id,))
                        
                        # Finalmente eliminar la licitacion
                        cur.execute("DELETE FROM licitaciones WHERE id = %s", (licitacion_id,))
                        
                        cur.execute("RELEASE SAVEPOINT pre_delete")
                    except Exception as db_cascade_error:
                        cur.execute("ROLLBACK TO SAVEPOINT pre_delete")
                        print(f"⚠️ Error intentando borrar manual en cascada, cayendo a DELETE normal: {db_cascade_error}")
                        # Intentar eliminar directamente (confiando en ON DELETE CASCADE)
                        cur.execute("DELETE FROM licitaciones WHERE id = %s", (licitacion_id,))

            return ApiResponse.ok(message="Licitación eliminada exitosamente")

        except Exception as e:
            print(f"ERROR DeleteLicitacionService: {str(e)}")
            return ApiResponse.fail(message="No se pudo eliminar la licitación", error=str(e))
        finally:
            conn.close()

    @staticmethod
    def bulk_delete_licitaciones(licitacion_ids: List[str]) -> ApiResponse:
        success_count = 0
        errores = []
        for lid in licitacion_ids:
            try:
                res = DeleteLicitacionService.delete_licitacion(lid)
                if res.success:
                    success_count += 1
                else:
                    errores.append(f"UUID {lid}: {res.message}")
            except Exception as e:
                errores.append(f"UUID {lid}: {str(e)}")
                
        print(f"✅ Borrado masivo finalizado. Éxitos: {success_count}. Errores: {len(errores)}")
        if errores and success_count == 0:
            return ApiResponse.fail(message="Fallo general al eliminar licitaciones", error=str(errores))
        elif errores:
            return ApiResponse.ok(message=f"Se eliminaron {success_count} licitaciones con algunos errores: {str(errores)}")
        return ApiResponse.ok(message=f"Se eliminaron las {success_count} licitaciones correctamente.")
