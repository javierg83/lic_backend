from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List
from .service import LicitacionNewService
from .schemas import LicitacionNewResponse
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required

router = APIRouter()

@router.post("/new", response_model=ApiResponse[LicitacionNewResponse])
async def create_licitacion(
    nombre: str = Form(...),
    files: List[UploadFile] = File(...),
    user_data: dict = Depends(auth_required)
):
    if user_data.get("rol") != "admin":
        raise HTTPException(status_code=403, detail="Acción permitida solo para administradores globales")
    return await LicitacionNewService.process(nombre, files)
