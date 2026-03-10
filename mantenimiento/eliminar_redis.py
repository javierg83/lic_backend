import sys
import os
import redis

# Agregar el directorio padre al path para importar src.core.config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD

def clear_redis_keys(prefixes):
    try:
        # Conexión a Redis utilizando la misma configuración de lic_backend
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        print("Conectado a Redis exitosamente.\n")
        
        total_deleted = 0
        
        for prefix in prefixes:
            patterns = [
                f"doc_raw:{prefix}*",
                f"doc_raw_page:{prefix}*"
            ]
            
            for pattern in patterns:
                # Usar SCAN iterativamente para no bloquear el hilo de Redis
                cursor = 0
                keys_to_delete = []
                while True:
                    cursor, keys = r.scan(cursor=cursor, match=pattern, count=100)
                    if keys:
                        keys_to_delete.extend(keys)
                    if cursor == 0:
                        break
                
                if keys_to_delete:
                    # Dividir en lotes para evitar enviar un comando delete gigante
                    batch_size = 500
                    for i in range(0, len(keys_to_delete), batch_size):
                        batch = keys_to_delete[i:i+batch_size]
                        r.delete(*batch)
                    
                    print(f"✅ Prefix '{prefix}': Eliminadas {len(keys_to_delete)} llaves para el patrón {pattern}")
                    total_deleted += len(keys_to_delete)
                else:
                    print(f"ℹ️ Prefix '{prefix}': No se encontraron llaves para el patrón {pattern}")

        print(f"\n🚀 Proceso finalizado. Total de llaves eliminadas: {total_deleted}")

    except Exception as e:
        print(f"❌ Error al conectar o procesar Redis: {e}")

if __name__ == "__main__":
    codigos_a_borrar = [f"{i}_" for i in range(1, 41)]
    print("Se buscarán y eliminarán llaves doc_raw y doc_raw_page que comiencen con los siguientes prefijos:")
    print(codigos_a_borrar)
    print("-" * 50)
    
    confirmacion = input("\n¿Estás seguro de que deseas continuar con la eliminación masiva? (s/n): ")
    
    if confirmacion.lower() in ('s', 'si', 'sí', 'y', 'yes'):
        clear_redis_keys(codigos_a_borrar)
    else:
        print("Operación cancelada. No se borró nada.")
