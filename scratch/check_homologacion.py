import psycopg2, os
from dotenv import load_dotenv
load_dotenv(override=True)
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# 1. Columnas reales de items_licitacion
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_schema = 'public' AND table_name = 'items_licitacion'
    ORDER BY ordinal_position
""")
print("=== items_licitacion columnas ===")
for (col,) in cur.fetchall():
    print(f"  {col}")

# 2. Items de la licitacion más reciente
cur.execute("""
    SELECT il.nombre_item
    FROM items_licitacion il
    JOIN licitaciones_descargadas l ON l.id = il.licitacion_id
    ORDER BY l.fecha_carga DESC, il.id
    LIMIT 10
""")
print("\n=== Items extraidos ===")
for row in cur.fetchall():
    print(f"  - {row[0]}")

# 3. Catalogo dental
cur.execute("""SELECT codigo, nombre_producto FROM cliente_productos 
    WHERE cliente_id = 'a1000000-0000-0000-0000-000000000001' ORDER BY codigo""")
print("\n=== Catalogo Dental Sur ===")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
