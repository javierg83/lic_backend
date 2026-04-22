from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .service import ClienteProductosService
from .schemas import UploadProductosResponse

router = APIRouter()

@router.post("/{cliente_id}/productos/upload_csv", response_model=ApiResponse[UploadProductosResponse])
async def upload_csv_productos(
    cliente_id: str,
    file: UploadFile = File(...),
    user_data: dict = Depends(auth_required)
):
    # Verificación de seguridad
    if user_data.get("rol") != "admin" and user_data.get("cliente_id") != cliente_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para alterar el catálogo de otro cliente")
        
    resultado = await ClienteProductosService.upload_csv(cliente_id, file)
    
    return ApiResponse.ok(
        data=resultado,
        message=f"Catálogo procesado: {resultado.total_insertados} productos añadidos."
    )
