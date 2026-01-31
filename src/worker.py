import json
import redis
import time
from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, REDIS_DB

def run_worker():
    # Asegurar tipos de datos correctos para Redis
    redis_port = int(REDIS_PORT)
    redis_db = int(REDIS_DB)

    print(f"🚀 Iniciando Worker de Licitaciones...")
    print(f"📡 Conectando a Redis en {REDIS_HOST}:{redis_port} (DB: {redis_db})...")

    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=redis_port,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            db=redis_db,
            decode_responses=True
        )

        # Verificar conexión
        r.ping()
        print("✅ Conexión a Redis exitosa.")
        print("📥 Esperando mensajes en 'document_queue'...")

        while True:
            # BRPOP bloquea hasta que hay un elemento en la lista
            # Retorna una tupla (nombre_cola, valor)
            result = r.brpop("document_queue", timeout=0)
            
            if result:
                queue_name, message_json = result
                try:
                    data = json.loads(message_json)
                    licitacion_id = data.get("licitacion_id")
                    timestamp = data.get("timestamp")

                    print(f"\n🔔 [NUEVO MENSAJE] Licitación ID: {licitacion_id}")
                    print(f"⏰ Recibido a: {timestamp}")
                    
                    # AQUÍ: Lógica para procesar los documentos de la licitación
                    # Por ejemplo: llamar a un servicio que extraiga texto, valide reglas, etc.
                    print(f"⚙️ Procesando archivos para la licitación {licitacion_id}...")
                    time.sleep(2) # Simulación de procesamiento
                    print(f"✅ Procesamiento completado para licitación {licitacion_id}")

                except json.JSONDecodeError:
                    print(f"⚠️ Error al decodificar mensaje: {message_json}")
                except Exception as e:
                    print(f"❌ Error procesando mensaje: {str(e)}")

    except Exception as e:
        print(f"💥 Error crítico en el Worker: {str(e)}")

if __name__ == "__main__":
    run_worker()
