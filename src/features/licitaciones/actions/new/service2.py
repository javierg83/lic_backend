import os
import shutil
import hashlib
import sqlite3
from datetime import datetime
from fastapi import UploadFile
from src.core.responses import ApiResponse
from src.core.config import DB_PATH, UPLOAD_DIR, REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, REDIS_DB
import redis
import json
from .schemas import DocumentUploadOut


class DocumentUploadService:
    @staticmethod
    async def process(file: UploadFile, licitacion_id: int) -> ApiResponse[DocumentUploadOut]:
        try:
            # Asegurar que el directorio de subidas exista
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            file_path = os.path.join(UPLOAD_DIR, file.filename)
            
            # Guardar el archivo y calcular checksum simultáneamente
            sha256_hash = hashlib.sha256()
            with open(file_path, "wb") as buffer:
                # Leer en trozos para archivos grandes
                while content := await file.read(4096):
                    buffer.write(content)
                    sha256_hash.update(content)
            
            checksum = sha256_hash.hexdigest()
            file_size = os.path.getsize(file_path)
            upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Guardar en base de datos
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documentos (filename, upload_date, checksum, size, estado)
                VALUES (?, ?, ?, ?, ?)
            ''', (file.filename, upload_date, checksum, file_size, "pendiente"))
            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Notificar al Worker via Redis
            try:
                # Asegurar tipos de datos correctos
                redis_port = int(REDIS_PORT)
                redis_db = int(REDIS_DB)
                
                print(f"DEBUG: Intentando conectar a Redis en {REDIS_HOST}:{redis_port} (DB: {redis_db})")
                r = redis.Redis(
                    host=REDIS_HOST,
                    port=redis_port,
                    username=REDIS_USERNAME,
                    password=REDIS_PASSWORD,
                    db=redis_db,
                    decode_responses=True
                )
                
                # Verificar conexión explícitamente
                pong = r.ping()
                print(f"DEBUG: PING Redis: {pong}")
                
                queue_data = {
                    "licitacion_id": licitacion_id,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"DEBUG: Enviando a 'document_queue': {json.dumps(queue_data)}")
                result = r.lpush("document_queue", json.dumps(queue_data))
                print(f"📢 Mensaje enviado (Resultado LPUSH: {result}) para Licitación ID: {licitacion_id}")
            except Exception as redis_err:
                print(f"⚠️ Error CRÍTICO en Redis: {str(redis_err)}")
                import traceback
                traceback.print_exc()

            result = DocumentUploadOut(
                filename=file.filename,
                size=file_size,
                success=True
            )

            return ApiResponse(
                success=True,
                message="Documento subido y registrado correctamente",
                data=result
            )
        except Exception as e:
            return ApiResponse(
                success=False,
                message="Error al procesar el documento",
                error=str(e)
            )
