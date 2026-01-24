import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    # Obtener variables de entorno del .env
    host = os.getenv("DB_POSTGRES_HOST", "localhost")
    port = os.getenv("DB_POSTGRES_PORT", "5432")
    database = os.getenv("DB_POSTGRES_NAME", "postgres")
    user = os.getenv("DB_POSTGRES_USER", "postgres")
    password = os.getenv("DB_POSTGRES_PASSWORD", "postgres")

    print(f"--- Intentando conectar a PostgreSQL ---")
    print(f"Host: {host}")
    print(f"Puerto: {port}")
    print(f"Base de Datos: {database}")
    print(f"Usuario: {user}")

    connection = None
    try:
        # Intentar establecer la conexión
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5
        )

        # Crear un cursor para ejecutar una consulta simple
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("\n✅ Conexión exitosa!")
        print(f"Versión de PostgreSQL: {db_version[0]}")

        # Cerrar el cursor
        cursor.close()

    except Exception as error:
        print(f"\n❌ Error al conectar a PostgreSQL: {error}")
        print("\nSugerencia: Revisa que las variables de entorno en el archivo .env sean correctas y que el servidor PostgreSQL esté corriendo.")
        
    finally:
        # Cerrar la conexión si se estableció
        if connection:
            connection.close()
            print("--- Conexión cerrada ---")

if __name__ == "__main__":
    test_connection()
