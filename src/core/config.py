
import os
from dotenv import load_dotenv

load_dotenv()



UPLOAD_DIR = os.getenv('UPLOAD_DIR')
if not UPLOAD_DIR:
    RuntimeError("Falta la variable de entorno UPLOADS_DIR")


DB_PATH = os.getenv('DB_PATH')

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_DB = os.getenv('REDIS_DB', '0')
