
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    @staticmethod
    def get_connection():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
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
