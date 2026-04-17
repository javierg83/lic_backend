import os
import sys
import psycopg2
from dotenv import load_dotenv

# Asegurar que estamos en el directorio de backend para leer el .env correcto
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

load_dotenv(os.path.join(backend_dir, '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: No se encontró DATABASE_URL en el archivo .env")
    sys.exit(1)

def generar_esquema_sql():
    try:
        print("Conectando a la base de datos Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        output_file = os.path.join(backend_dir, "base_actual_supabase.sql")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- ==============================================================================\n")
            f.write("-- AUTO-GENERADO: ESQUEMA ACTUAL EN SUPABASE\n")
            f.write("-- Generado por exportar_esquema.py para contrastar con 100_full_schema_v3_compatible.sql\n")
            f.write("-- ==============================================================================\n\n")

            # 1. Obtener todas las tablas del esquema public
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tablas = cur.fetchall()

            if not tablas:
                print("No se encontraron tablas en el esquema public.")
                return

            for (tabla,) in tablas:
                f.write(f"-- TABLA: {tabla}\n")
                f.write(f"CREATE TABLE public.{tabla} (\n")

                # Obtener columnas
                cur.execute("""
                    SELECT column_name, data_type, character_maximum_length, column_default, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position;
                """, (tabla,))
                columnas = cur.fetchall()

                # Obtener Primary Keys
                cur.execute("""
                    SELECT c.column_name
                    FROM information_schema.table_constraints tc 
                    JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) 
                    JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                      AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                    WHERE constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public' AND tc.table_name = %s;
                """, (tabla,))
                pk_cols = [row[0] for row in cur.fetchall()]

                # Obtener Foreign Keys (Básico)
                cur.execute("""
                    SELECT kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
                    FROM information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND tc.table_name = %s;
                """, (tabla,))
                fk_cols = {row[0]: f"REFERENCES public.{row[1]}({row[2]})" for row in cur.fetchall()}

                col_defs = []
                for col in columnas:
                    col_name, data_type, max_len, default_val, is_nullable = col
                    
                    # Formatear el tipo
                    tipo = data_type
                    if tipo == 'character varying' and max_len:
                        tipo = f"VARCHAR({max_len})"
                    elif tipo == 'character varying':
                        tipo = "TEXT"
                    elif tipo == 'timestamp without time zone':
                        tipo = "TIMESTAMP"
                    elif tipo == 'timestamp with time zone':
                        tipo = "TIMESTAMPTZ"
                    elif tipo == 'numeric':
                        tipo = "NUMERIC"
                    
                    linea = f"    {col_name} {tipo}"
                    
                    if default_val:
                        linea += f" DEFAULT {default_val}"
                    if is_nullable == 'NO':
                        linea += " NOT NULL"
                    if col_name in pk_cols:
                        linea += " PRIMARY KEY"
                    if col_name in fk_cols:
                        linea += f" {fk_cols[col_name]}"
                        
                    col_defs.append(linea)
                
                f.write(",\n".join(col_defs) + "\n")
                f.write(");\n\n")

                # Obtener Índices
                cur.execute("""
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE schemaname = 'public' AND tablename = %s
                    AND indexname NOT IN (
                        SELECT constraint_name FROM information_schema.table_constraints 
                        WHERE table_name = %s AND constraint_type = 'PRIMARY KEY'
                    );
                """, (tabla, tabla))
                indices = cur.fetchall()
                
                for idx_name, idx_def in indices:
                    f.write(f"{idx_def};\n")
                
                f.write("\n\n")

        print(f"✅ ¡Éxito! El archivo se ha generado en: {output_file}")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error al conectar o extraer datos: {e}")

if __name__ == "__main__":
    generar_esquema_sql()
