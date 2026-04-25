from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .service import AdminClienteService
from .schemas import ClienteCreate, ClienteResponse, ClienteDetailResponse

router = APIRouter()

def admin_only(user_data: dict = Depends(auth_required)):
    if user_data.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado: Se requieren permisos de administrador.")
    return user_data

@router.get("/", response_model=ApiResponse[List[ClienteResponse]])
async def list_clientes(user_data: dict = Depends(admin_only)):
    resultado = AdminClienteService.get_all_clientes()
    return ApiResponse.ok(data=resultado)

@router.post("/", response_model=ApiResponse[ClienteResponse])
async def create_cliente(data: ClienteCreate, user_data: dict = Depends(admin_only)):
    resultado = AdminClienteService.create_cliente(data)
    return ApiResponse.ok(data=resultado, message="Cliente creado exitosamente")

@router.get("/{cliente_id}", response_model=ApiResponse[ClienteDetailResponse])
async def get_cliente(cliente_id: str, user_data: dict = Depends(admin_only)):
    resultado = AdminClienteService.get_cliente_detail(cliente_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return ApiResponse.ok(data=resultado)

@router.put("/usuarios/{username}/password")
async def update_password(username: str, data: dict, user_data: dict = Depends(admin_only)):
    new_password = data.get("password")
    if not new_password:
        raise HTTPException(status_code=400, detail="Contraseña no proporcionada")
    
    exito = AdminClienteService.update_user_password(username, new_password)
    if not exito:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return ApiResponse.ok(message="Contraseña actualizada exitosamente")

@router.post("/{cliente_id}/usuarios")
async def add_user_to_client(cliente_id: str, data: dict, user_data: dict = Depends(admin_only)):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username y Password son obligatorios")
    
    # Obtener nombre empresa para el nombre de usuario
    cliente = AdminClienteService.get_cliente_detail(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    exito = AdminClienteService.create_user_for_client(
        cliente_id, 
        username, 
        password, 
        f"Admin {cliente.nombre}"
    )
    
    if not exito:
        raise HTTPException(status_code=500, detail="Error creando usuario")
        
    return ApiResponse.ok(message="Usuario creado exitosamente")
