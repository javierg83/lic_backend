from fastapi import HTTPException
from src.core.security import create_access_token
from .schemas import LoginData

HARDCODED_USER = {
    "username": "usuario",
    "password": "password",
    "nombre_usuario": "Administrador"
}

class AuthService:
    @staticmethod
    def login(data: LoginData):
        username = data.username
        password = data.password

        if username != HARDCODED_USER["username"] or password != HARDCODED_USER["password"]:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        token = create_access_token({"sub": username})
        return {
            "access_token": token,
            "nombre_usuario": HARDCODED_USER["nombre_usuario"]
        }
