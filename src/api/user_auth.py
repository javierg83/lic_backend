
from pydantic import BaseModel
from src.core.security import create_access_token, verify_token
from fastapi import Header, Depends, HTTPException,APIRouter


router = APIRouter()

class LoginData(BaseModel):
    username: str
    password: str

HARDCODED_USER = {
    "username": "usuario",
    "password": "password",
    "nombre_usuario": "Administrador"
}


@router.post("/login")
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


def auth_required(authorization: str = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Convertir payload estándar ("sub") a lo que espera el backend
    return {
        "username": payload.get("sub")
    }