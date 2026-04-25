from fastapi import APIRouter, Depends, HTTPException
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .service import ClienteConfiguracionService
from .schemas import ClienteConfiguracionResponse, ClienteConfiguracionUpdate

router = APIRouter()

@router.get("/{cliente_id}/configuracion", response_model=ApiResponse[ClienteConfiguracionResponse])
async def get_configuracion(
    cliente_id: str,
    user_data: dict = Depends(auth_required)
):
    # Seguridad: Solo admin o el propio cliente
    if user_data.get("rol") != "admin" and user_data.get("cliente_id") != cliente_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver configuración de otro cliente")
        
    resultado = ClienteConfiguracionService.get_configuracion(cliente_id)
    return ApiResponse.ok(data=resultado)

@router.put("/{cliente_id}/configuracion", response_model=ApiResponse[ClienteConfiguracionResponse])
async def update_configuracion(
    cliente_id: str,
    data: ClienteConfiguracionUpdate,
    user_data: dict = Depends(auth_required)
):
    # Seguridad: Solo admin o el propio cliente
    if user_data.get("rol") != "admin" and user_data.get("cliente_id") != cliente_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar configuración de otro cliente")
        
    resultado = ClienteConfiguracionService.update_configuracion(cliente_id, data)
    return ApiResponse.ok(data=resultado, message="Configuración actualizada correctamente")
