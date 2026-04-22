from fastapi import HTTPException
from src.core.security import create_access_token
from .schemas import LoginData

from src.core.database import Database

class AuthService:
    @staticmethod
    def login(data: LoginData):
        username = data.username
        password = data.password

        query = "SELECT * FROM usuarios WHERE username = %s"
        user_row = Database.execute_query(query, (username,), fetch_all=False)

        if not user_row or user_row["password_hash"] != password:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # El rol se incluye en el token para evitar consultas extras si es necesario
        token = create_access_token({
            "sub": username, 
            "rol": user_row["rol"],
            "cliente_id": str(user_row.get("cliente_id", "")) if user_row.get("cliente_id") else None
        })
        
        return {
            "access_token": token,
            "nombre_usuario": user_row["nombre_usuario"],
            "rol": user_row["rol"],
            "cliente_id": str(user_row.get("cliente_id", "")) if user_row.get("cliente_id") else None
        }
