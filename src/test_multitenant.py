import os
import json
import psycopg2
import uuid
from dotenv import load_dotenv

load_dotenv(override=True)
DATABASE_URL = os.getenv('DATABASE_URL')

print("Conectando a Base de Datos:", DATABASE_URL)
conn = psycopg2.connect(DATABASE_URL)

try:
    with conn.cursor() as cur:
        # 1. Obtener Cliente Legacy
        cur.execute("SELECT id, nombre FROM clientes WHERE nombre = 'Cliente Global Inicial' LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("No se encontro cliente inicial")
            exit(1)
        
        cliente_id = str(row[0])
        print(f"Cliente ID: {cliente_id} ({row[1]})")

        # 2. Configurar preferencias (Limpiar antes para evitar duplicidad si no hay constraint)
        cur.execute("DELETE FROM cliente_preferencias WHERE cliente_id = %s", (cliente_id,))
        keywords = '["computadores", "tecnología", "test-kw"]'
        cur.execute("""
            INSERT INTO cliente_preferencias (cliente_id, palabras_clave_json)
            VALUES (%s, %s)
        """, (cliente_id, keywords))
        
        print("Preferencias de derivacion configuradas.")
        
        # 3. Subir Catálogo (Limpiar antes para el test)
        cur.execute("DELETE FROM cliente_productos WHERE cliente_id = %s", (cliente_id,))
        print("Subiendo catalogo directamente a BD (columnas: codigo, nombre_producto, descripcion, precio_referencial)...")
        cur.execute("""
            INSERT INTO cliente_productos (cliente_id, codigo, nombre_producto, descripcion, precio_referencial)
            VALUES 
            (%s, 'DOC001', 'Macbook Pro Test', 'Notebook para devs', 1200000),
            (%s, 'LT002', 'Lector Huella Tech', 'Huellero digital', 45000)
        """, (cliente_id, cliente_id))
        
        # 4. Insertar Licitación Fake
        fake_lic_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO licitaciones_descargadas (id, codigo_licitacion, nombre, descripcion, estado_publicacion, estado)
            VALUES (%s, %s, %s, %s, 'Publicada', 'PENDIENTE')
        """, (fake_lic_id, "TEST-KW-001", "Licitacion Test-KW", "Necesitamos computadores y tecnología para el colegio"))
        
        conn.commit()
        print(f"Licitacion fake creada: {fake_lic_id}")

        # 5. Encolar asíncronamente
        import redis
        REDIS_HOST = os.getenv("REDIS_HOST", "redis-17408.c283.us-east-1-4.ec2.redns.redis-cloud.com")
        REDIS_PORT = int(os.getenv("REDIS_PORT", 17408))
        REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        
        print("Enviando a homologation_queue directamente para el test...")
        r.rpush("homologation_queue", json.dumps({"licitacion_id": fake_lic_id, "cliente_id": cliente_id, "ai_provider": "google"}))
        print(f"Encolado en Homologation Queue para la lic_id: {fake_lic_id}")

except Exception as e:
    print("Test Error:", e)
    conn.rollback()
finally:
    conn.close()
