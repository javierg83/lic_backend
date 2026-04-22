import psycopg2, os
from dotenv import load_dotenv
load_dotenv(override=True)
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

tables_to_check = [
    'finanzas_licitacion',
    'gestion_licitaciones',
    'gestion_licitacion_documentos',
    'usuarios',
    'adjudicaciones_licitacion',
    'licitaciones_descargadas',
    'ai_token_usage_logs',
    'tabla_contenidos',
]

for table in tables_to_check:
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table,))
    cols = cur.fetchall()
    if cols:
        print(f"\n=== {table} ===")
        for col, dtype in cols:
            print(f"  {col}: {dtype}")
    else:
        print(f"\n=== {table} === *** NO EXISTE ***")

conn.close()
