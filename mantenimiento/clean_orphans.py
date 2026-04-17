import sys
import os
import redis

# Agregar el directorio padre al path para importar módulos de src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_USERNAME, REDIS_PASSWORD
from src.core.database import Database

def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

def fetch_active_db_records():
    print("📥 Consultando base de datos para obtener IDs activos...")
    
    # Obtenemos licitaciones que NO estén obsoletas
    query_lic = "SELECT id::text, id_interno::text FROM licitaciones WHERE obsoleto = FALSE;"
    lics = Database.execute_query(query_lic)
    valid_lic_ids = {row['id'] for row in lics}
    valid_lic_internos = {str(row['id_interno']) for row in lics if row['id_interno'] is not None}
    
    # Obtenemos archivos que NO estén obsoletos
    query_doc = "SELECT id::text, id_interno::text FROM licitacion_archivos WHERE obsoleto = FALSE;"
    docs = Database.execute_query(query_doc)
    valid_doc_ids = {row['id'] for row in docs}
    valid_doc_internos = {str(row['id_interno']) for row in docs if row['id_interno'] is not None}
    
    return valid_lic_ids, valid_lic_internos, valid_doc_ids, valid_doc_internos

def analyze_and_clean_redis():
    try:
        r = get_redis_client()
        r.ping()
        print("✅ Conectado a Redis exitosamente.")
    except Exception as e:
        print(f"❌ Error al conectar a Redis: {e}")
        return

    try:
        valid_lic_ids, valid_lic_internos, valid_doc_ids, valid_doc_internos = fetch_active_db_records()
        print(f"📊 Licitaciones válidas en BD: {len(valid_lic_ids)} (IDs) / {len(valid_lic_internos)} (id_interno)")
    except Exception as e:
        print(f"❌ Error al conectar a la Base de Datos: {e}")
        return

    patterns = ["pdf:*", "doc_raw:*", "doc_raw_page:*"]
    keys_to_delete = []
    
    total_scanned = 0
    orphaned_lic = 0
    orphaned_doc = 0
    
    for pattern in patterns:
        cursor = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match=pattern, count=500)
            for key in keys:
                total_scanned += 1
                is_orphan = False
                
                parts = key.split(":")
                
                if pattern == "pdf:*":
                    if len(parts) >= 3:
                        lic_id = parts[1]
                        if lic_id != "SIN_LICITACION_ID" and lic_id not in valid_lic_ids:
                            is_orphan = True
                            orphaned_lic += 1
                            
                elif pattern.startswith("doc_raw"):
                    if len(parts) >= 2:
                        doc_id = parts[1]
                        
                        # doc_id aquí podría ser un id_interno (ej: "187_326_archivo.pdf") o un UUID
                        subparts = doc_id.split("_")
                        
                        # Si tiene partes separadas por _ y la primera es número, suele ser lic_id_interno
                        if len(subparts) >= 2 and subparts[0].isdigit():
                            lic_id_interno = subparts[0]
                            if lic_id_interno not in valid_lic_internos:
                                is_orphan = True
                                orphaned_lic += 1
                        
                        # Si doc_id parece UUID
                        elif len(doc_id) == 36 and '-' in doc_id:
                            if doc_id not in valid_doc_ids and doc_id not in valid_lic_ids:
                                is_orphan = True
                                orphaned_doc += 1

                if is_orphan:
                    keys_to_delete.append(key)
                    
            if cursor == 0:
                break

    print("\n" + "="*50)
    print("📈 RESULTADOS DEL ANÁLISIS REDIS vs SUPABASE")
    print("="*50)
    print(f"Total de llaves fragmentadas escaneadas: {total_scanned}")
    print(f"Llaves huérfanas por Licitación Inexistente: {orphaned_lic}")
    print(f"Llaves huérfanas por Archivo Inexistente: {orphaned_doc}")
    print(f"TOTAL DE LLAVES A ELIMINAR: {len(keys_to_delete)}")
    
    if keys_to_delete:
        print("\nEjemplo de llaves huérfanas:")
        for k in keys_to_delete[:10]:
            print(f" - {k}")
            
        confirm = input(f"\n⚠️ ¿Estás seguro de que deseas ELIMINAR {len(keys_to_delete)} llaves descolgadas irreversiblemente? (s/n): ")
        if confirm.lower() in ('s', 'si', 'sí', 'y', 'yes'):
            # Ejecutar eliminación por lotes
            batch_size = 500
            for i in range(0, len(keys_to_delete), batch_size):
                batch = keys_to_delete[i:i+batch_size]
                r.delete(*batch)
            print("🚀 Limpieza finalizada con éxito.")
        else:
            print("Operación cancelada. El cluster Redis está intacto.")
    else:
        print("Todo en orden, no hay llaves descolgadas o huérfanas en Redis.")


if __name__ == "__main__":
    analyze_and_clean_redis()
