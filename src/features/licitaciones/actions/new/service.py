import os
import hashlib
from typing import List
from fastapi import UploadFile
from src.core.database import Database
from src.core.responses import ApiResponse
from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, REDIS_DB
import redis
import json
import traceback
from datetime import datetime
from .schemas import LicitacionNewResponse, FileValidationResult
from src.constants.states import FileStatus

class LicitacionNewService:
    @staticmethod
    async def process(nombre: str, files: List[UploadFile], tipo_licitacion: str = 'LICITACION_PUBLICA') -> ApiResponse[LicitacionNewResponse]:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        storage_path = os.getenv("FILE_STORAGE", "storage")
        max_size_mb = int(os.getenv("FILE_MAX_SIZE", "1"))
        max_size_bytes = max_size_mb * 1024 * 1024
        allowed_extensions = os.getenv("FILE_EXTENSION", ".pdf,.doc,.docx,.txt,.xlsx,.xls,.csv,.json").lower().split(",")
        
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        validation_results = []
        valid_files_data = []
        any_error = False

        # Pre-process and validate all files
        hashes_in_batch = set()

        for file in files:
            file_ext = os.path.splitext(file.filename)[1].lower()
            content = await file.read()
            file_size = len(content)
            file_hash = hashlib.md5(content).hexdigest()
            await file.seek(0) # Reset pointer

            print(f"[DEBUG] Validando archivo: {file.filename}, Ext: {file_ext}")
            
            file_error = None
            if file_ext not in allowed_extensions:
                file_error = f"Extensión {file_ext} no permitida. Permitidas: {', '.join(allowed_extensions)}"
                print(f"[ERROR] Validación fallida por extensión: {file_ext}")
            elif file_size > max_size_bytes:
                file_error = f"El archivo excede el tamaño máximo de {max_size_mb}MB"
                print(f"[ERROR] Validación fallida por tamaño: {file_size} bytes")
            elif file_hash in hashes_in_batch:
                file_error = "Archivo duplicado en el mismo envío"
                print(f"[ERROR] Validación fallida por duplicidad de hash en el lote")
            
            if file_error:
                validation_results.append(FileValidationResult(nombre=file.filename, valido=False, error=file_error))
                any_error = True
            else:
                hashes_in_batch.add(file_hash)
                validation_results.append(FileValidationResult(nombre=file.filename, valido=True))
                valid_files_data.append({
                    "filename": file.filename,
                    "content": content,
                    "size": file_size,
                    "hash": file_hash,
                    "content_type": file.content_type
                })

        if any_error:
            print(f"[WARNING] Proceso abortado: Uno o más archivos no cumplen requisitos. {validation_results}")
            return ApiResponse.fail(
                message="Uno o más archivos no cumplen con los requisitos",
                data=LicitacionNewResponse(nombre=nombre, archivos_procesados=validation_results)
            )
        
        print(f"[DEBUG] Todos los archivos ({len(valid_files_data)}) pasaron validación.")

        # Database transaction
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Insert Licitacion
                    cur.execute(
                        "INSERT INTO licitaciones (nombre, estado, tipo_licitacion) VALUES (%s, 'PENDIENTE', %s) RETURNING id, id_interno",
                        (nombre, tipo_licitacion)
                    )
                    row = cur.fetchone()
                    licitacion_id = row[0]
                    licitacion_id_interno = row[1]

                    # Insert Files
                    for i, file_data in enumerate(valid_files_data):
                        # ... (rest of the loop)
                        file_path = os.path.join(storage_path, f"{licitacion_id}_{file_data['filename']}")
                        
                        # Save to disk
                        with open(file_path, "wb") as f:
                            f.write(file_data["content"])

                        cur.execute(
                            """
                            INSERT INTO licitacion_archivos 
                            (licitacion_id, nombre_archivo_org, ruta_almacenamiento, tipo_contenido, peso_bytes, hash_md5, estado_procesamiento)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """,
                            (licitacion_id, file_data["filename"], file_path, file_data["content_type"], file_data["size"], file_data["hash"], FileStatus.PENDIENTE)
                        )
            
            # Notificar al Worker via Redis
            try:
                r = redis.Redis(
                    host=REDIS_HOST,
                    port=int(REDIS_PORT),
                    username=REDIS_USERNAME,
                    password=REDIS_PASSWORD,
                    db=int(REDIS_DB),
                    decode_responses=True
                )
                queue_data = {
                    "licitacion_id": licitacion_id,
                    "timestamp": datetime.now().isoformat()
                }
                r.lpush("document_queue", json.dumps(queue_data))
                print(f"📢 Mensaje enviado a Redis para Licitación ID: {licitacion_id}")
            except Exception as redis_err:
                print(f"⚠️ Error al notificar a Redis: {redis_err}")
                traceback.print_exc()

            return ApiResponse.ok(
                data=LicitacionNewResponse(id=licitacion_id, id_interno=licitacion_id_interno, nombre=nombre, archivos_procesados=validation_results),
                message="Licitación creada exitosamente"
            )

        except Exception as e:
            # Cleanup files on disk if DB fails? (Optional, here focusing on transaction)
            print("❌ Error CRITICO en LicitacionNewService:")
            print(f"Error: {e}")
            traceback.print_exc()
            return ApiResponse.fail(
                message="Error al guardar la licitación en la base de datos",
                error=str(e)
            )
        finally:
            conn.close()
