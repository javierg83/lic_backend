from fastapi import APIRouter, BackgroundTasks
from src.core.responses import ApiResponse
from .service import DeleteLicitacionService
from .schemas import BulkDeleteRequest

router = APIRouter()

@router.delete("/{licitacion_id}", response_model=ApiResponse)
async def delete_licitacion(licitacion_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(DeleteLicitacionService.delete_licitacion, licitacion_id)
    return ApiResponse.ok(message="Eliminación iniciada. El proceso de borrado se completará en segundo plano.")

@router.post("/bulk-delete", response_model=ApiResponse)
async def bulk_delete_licitaciones(payload: BulkDeleteRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(DeleteLicitacionService.bulk_delete_licitaciones, payload.ids)
    return ApiResponse.ok(message=f"Eliminación masiva iniciada para {len(payload.ids)} licitaciones. El proceso se completará en segundo plano.")
