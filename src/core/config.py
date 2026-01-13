
import os
from dotenv import load_dotenv

load_dotenv()



UPLOAD_DIR = os.getenv('UPLOAD_DIR')
if not UPLOAD_DIR:
    RuntimeError("Falta la variable de entorno UPLOADS_DIR")


DB_PATH = os.getenv('DB_PATH')
