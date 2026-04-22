from fastapi import APIRouter, Depends, HTTPException
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .service import ClientePreferenciasService
from .schemas import ClientePreferenciasResponse, ClientePreferenciasUpdate

router = APIRouter()

@router.get("/{cliente_id}/preferencias", response_model=ApiResponse[ClientePreferenciasResponse])
async def get_preferencias(
    cliente_id: str,
    user_data: dict = Depends(auth_required)
):
    # Seguridad: Solo admin o el propio cliente
    if user_data.get("rol") != "admin" and user_data.get("cliente_id") != cliente_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver preferencias de otro cliente")
        
    resultado = ClientePreferenciasService.get_preferencias(cliente_id)
    return ApiResponse.ok(data=resultado)

@router.put("/{cliente_id}/preferencias", response_model=ApiResponse[ClientePreferenciasResponse])
async def update_preferencias(
    cliente_id: str,
    data: ClientePreferenciasUpdate,
    user_data: dict = Depends(auth_required)
):
    # Seguridad: Solo admin o el propio cliente
    if user_data.get("rol") != "admin" and user_data.get("cliente_id") != cliente_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para modificar preferencias de otro cliente")
        
    resultado = ClientePreferenciasService.update_preferencias(cliente_id, data)
    return ApiResponse.ok(data=resultado, message="Preferencias actualizadas correctamente")
