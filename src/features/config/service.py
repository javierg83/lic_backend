import os
from fastapi import UploadFile
from src.core.responses import ApiResponse

class ConfigService:
    @staticmethod
    async def upload_catalog(file: UploadFile) -> ApiResponse:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        supabase_bucket = os.getenv("SUPABASE_BUCKET", "licitaciones")
        
        if not supabase_url or not supabase_key:
            return ApiResponse.fail(message="Supabase no está configurado en el backend")
            
        if not file.filename.endswith(('.xls', '.xlsx')):
            return ApiResponse.fail(message="El archivo debe ser un Excel (.xls o .xlsx)")

        try:
            content = await file.read()
            from supabase import create_client, Client
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Attempt to remove the old file first to simulate upsert and prevent python client hangs
            try:
                supabase.storage.from_(supabase_bucket).remove(["catalogos/productos.xlsx"])
            except Exception:
                pass
            
            supabase.storage.from_(supabase_bucket).upload(
                path="catalogos/productos.xlsx",
                file=content,
                file_options={"content-type": file.content_type}
            )
            return ApiResponse.ok(message="Catálogo subido exitosamente a Supabase")
        except Exception as e:
            print(f"ERROR ConfigService.upload_catalog: {str(e)}")
            return ApiResponse.fail(message="Error al subir el catálogo a Supabase", error=str(e))
