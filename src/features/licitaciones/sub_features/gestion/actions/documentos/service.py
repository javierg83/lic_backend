import os
from fastapi import UploadFile
from typing import Optional
from uuid import UUID
from psycopg2.extras import RealDictCursor
from typing import List
from src.core.database import Database
from src.core.responses import ApiResponse
from .schemas import GestionDocumentoRequest, GestionDocumentoResponse

class GestionDocumentosService:
    @staticmethod
    async def process_get(gestion_id: UUID) -> ApiResponse[List[GestionDocumentoResponse]]:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT id, gestion_id, tipo_documento, nombre_archivo, ruta_archivo, fecha_subida, usuario, observacion
                        FROM gestion_licitacion_documentos
                        WHERE gestion_id = %s
                        ORDER BY fecha_subida DESC
                        """,
                        (str(gestion_id),)
                    )
                    rows = cur.fetchall()
                    
                    datos = [
                        GestionDocumentoResponse(
                            id=row['id'],
                            gestion_id=row['gestion_id'],
                            tipo_documento=row['tipo_documento'],
                            nombre_archivo=row['nombre_archivo'],
                            ruta_archivo=row['ruta_archivo'],
                            fecha_subida=row['fecha_subida'],
                            usuario=row['usuario'],
                            observacion=row['observacion']
                        ) for row in rows
                    ]
            
            return ApiResponse.ok(
                data=datos,
                message="Documentos de gestión obtenidos exitosamente"
            )

        except Exception as e:
            print(f"ERROR GestionDocumentosService.process_get: {str(e)}")
            return ApiResponse.fail(
                message="No se pudieron cargar los documentos.",
                error=str(e)
            )
        finally:
            conn.close()

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        import unicodedata
        import re
        # Normalizar para eliminar acentos
        nfkd_form = unicodedata.normalize('NFKD', filename)
        only_ascii = nfkd_form.encode('ascii', 'ignore').decode('ascii')
        # Reemplazar espacios y caracteres raros por guiones bajos
        sanitized = re.sub(r'[^\w\.-]', '_', only_ascii)
        return sanitized

    @staticmethod
    async def process_post(gestion_id: UUID, file: UploadFile, tipo_documento: str, observacion: Optional[str]) -> ApiResponse[GestionDocumentoResponse]:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "licitaciones")

        original_filename = file.filename
        sanitized_filename = GestionDocumentosService._sanitize_filename(original_filename)
        content = await file.read()
        file_path = f"gestion/{gestion_id}/{sanitized_filename}"
        public_url = file_path # Fallback

        if supabase_url and supabase_key:
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            try:
                # Subir archivo
                supabase.storage.from_(supabase_bucket).upload(
                    path=file_path,
                    file=content,
                    file_options={"content-type": file.content_type}
                )
                print(f"✅ Archivo subido a Supabase: {file_path}")
                # En modo privado, guardamos el path lógico para generar URLs firmadas luego
                public_url = file_path 
            except Exception as e:
                # Si falló por existir, igual mantenemos el path
                print(f"❌ Error al subir a Supabase: {e}")
                public_url = file_path

        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        INSERT INTO gestion_licitacion_documentos (
                            gestion_id, tipo_documento, nombre_archivo, ruta_archivo, fecha_subida, observacion
                        ) VALUES (
                            %s, %s, %s, %s, timezone('utc'::text, now()), %s
                        ) RETURNING id, gestion_id, tipo_documento, nombre_archivo, ruta_archivo, fecha_subida, usuario, observacion
                        """,
                        (
                            str(gestion_id),
                            tipo_documento,
                            original_filename, # Mantenemos el nombre original para mostrar en la tabla
                            public_url,
                            observacion
                        )
                    )
                    row = cur.fetchone()
                    
                    datos = GestionDocumentoResponse(
                        id=row['id'],
                        gestion_id=row['gestion_id'],
                        tipo_documento=row['tipo_documento'],
                        nombre_archivo=row['nombre_archivo'],
                        ruta_archivo=row['ruta_archivo'],
                        fecha_subida=row['fecha_subida'],
                        usuario=row['usuario'],
                        observacion=row['observacion']
                    )
                    
            return ApiResponse.ok(
                data=datos,
                message="Documento de gestión registrado exitosamente"
            )

        except Exception as e:
            print(f"ERROR GestionDocumentosService.process_post: {str(e)}")
            return ApiResponse.fail(
                message="No se pudo registrar el documento en BD.",
                error=str(e)
            )
        finally:
            conn.close()

    @staticmethod
    async def process_download(documento_id: UUID) -> Optional[str]:
        """
        Obtiene una URL firmada de Supabase para un documento específico.
        """
        from dotenv import load_dotenv
        load_dotenv(override=True)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "licitaciones")

        if not supabase_url or not supabase_key:
            return None

        conn = Database.get_connection()
        try:
            file_path = None
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT ruta_archivo FROM gestion_licitacion_documentos WHERE id = %s", (str(documento_id),))
                row = cur.fetchone()
                if row:
                    file_path = row['ruta_archivo']

            if not file_path:
                return None

            # Si ya es una URL absoluta (legacy de pruebas anteriores), la devolvemos tal cual
            if file_path.startswith("http"):
                return file_path

            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Generar URL firmada válida por 60 segundos
            # Usar create_signed_url para buckets privados
            res = supabase.storage.from_(supabase_bucket).create_signed_url(file_path, 60)
            
            # El SDK de supabase-py suele devolver un string directamente o un dict con 'signedURL'
            if isinstance(res, dict):
                return res.get('signedURL') or res.get('signed_url')
            return str(res)

        except Exception as e:
            print(f"ERROR GestionDocumentosService.process_download: {str(e)}")
            return None
        finally:
            conn.close()

    @staticmethod
    async def process_delete(documento_id: UUID) -> ApiResponse:
        """
        Elimina físicamente el archivo de Supabase Storage y el registro de la BD.
        """
        from dotenv import load_dotenv
        load_dotenv(override=True)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "licitaciones")

        conn = Database.get_connection()
        try:
            with conn:
                file_path = None
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 1. Obtener la ruta antes de borrar
                    cur.execute("SELECT ruta_archivo FROM gestion_licitacion_documentos WHERE id = %s", (str(documento_id),))
                    row = cur.fetchone()
                    if not row:
                        return ApiResponse.fail(message="Documento no encontrado", status_code=404)
                    
                    file_path = row['ruta_archivo']

                    # 2. Eliminar de Supabase (si no es una URL legacy externa)
                    if file_path and not file_path.startswith("http") and supabase_url and supabase_key:
                        from supabase import create_client, Client
                        supabase: Client = create_client(supabase_url, supabase_key)
                        try:
                            # Intenta borrar el objeto del bucket
                            supabase.storage.from_(supabase_bucket).remove([file_path])
                            print(f"🗑️ Archivo eliminado de Supabase: {file_path}")
                        except Exception as storage_err:
                            print(f"⚠️ Error al eliminar de Storage (continuando): {storage_err}")

                    # 3. Eliminar de la Base de Datos
                    cur.execute("DELETE FROM gestion_licitacion_documentos WHERE id = %s", (str(documento_id),))
                    
            return ApiResponse.ok(message="Documento eliminado exitosamente")

        except Exception as e:
            print(f"ERROR GestionDocumentosService.process_delete: {str(e)}")
            return ApiResponse.fail(message="No se pudo eliminar el documento", error=str(e))
        finally:
            conn.close()
