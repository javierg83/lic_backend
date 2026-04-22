from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from src.core.responses import ApiResponse
from .service import DeleteLicitacionService
from .schemas import BulkDeleteRequest
from src.features.auth.dependencies import auth_required

router = APIRouter()

@router.delete("/{licitacion_id}", response_model=ApiResponse)
async def delete_licitacion(
    licitacion_id: str, 
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(auth_required)
):
    if user_data.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acción permitida solo para administradores globales")
    background_tasks.add_task(DeleteLicitacionService.delete_licitacion, licitacion_id)
    return ApiResponse.ok(message="Eliminación iniciada. El proceso de borrado se completará en segundo plano.")

@router.post("/bulk-delete", response_model=ApiResponse)
async def bulk_delete_licitaciones(
    payload: BulkDeleteRequest, 
    background_tasks: BackgroundTasks,
    user_data: dict = Depends(auth_required)
):
    if user_data.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acción permitida solo para administradores globales")
    background_tasks.add_task(DeleteLicitacionService.bulk_delete_licitaciones, payload.ids)
    return ApiResponse.ok(message=f"Eliminación masiva iniciada para {len(payload.ids)} licitaciones. El proceso se completará en segundo plano.")
