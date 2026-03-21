
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

COMPRA_AGIL_BEARER = os.getenv('COMPRA_AGIL_BEARER')
COMPRA_AGIL_USER_KEY = os.getenv('COMPRA_AGIL_USER_KEY')
COMPRA_AGIL_API_KEY = os.getenv('COMPRA_AGIL_API_KEY')

# Precios de IA en USD por 1,000,000 de tokens
USD_TO_CLP = 930
AI_MODEL_PRICES = {
    "gpt-4o": {
        "input": 5.0,
        "output": 15.0
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },
    "text-embedding-3-small": {
        "input": 0.02,
        "output": 0.02 # Los embeddings suelen cobrar igual por todo
    }
}
