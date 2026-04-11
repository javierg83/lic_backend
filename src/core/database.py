
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    @staticmethod
    def get_connection():
        try:
            database_url = os.getenv("DATABASE_URL")
            
            if database_url:
                print("[DB] Usando DATABASE_URL")
                return psycopg2.connect(database_url)
                
            print("[DB] Usando configuración local por variables separadas")
            return psycopg2.connect(
                host=os.getenv("DB_POSTGRES_HOST"),
                dbname=os.getenv("DB_POSTGRES_DB"),
                user=os.getenv("DB_POSTGRES_USER"),
                password=os.getenv("DB_POSTGRES_PASSWORD"),
                port=os.getenv("DB_POSTGRES_PORT", "5432")
            )
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise e

    @staticmethod
    def execute_query(query, params=None, fetch_all=True):
        conn = Database.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch_all:
                    return cur.fetchall()
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def execute_non_query(query, params=None):
        conn = Database.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
        finally:
            conn.close()
