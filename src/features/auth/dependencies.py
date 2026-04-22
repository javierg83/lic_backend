from fastapi import Header, HTTPException
from src.core.security import verify_token

def auth_required(authorization: str = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return {
        "username": payload.get("sub"),
        "rol": payload.get("rol"),
        "cliente_id": payload.get("cliente_id")
    }
