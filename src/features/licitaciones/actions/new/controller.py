from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List
from .service import LicitacionNewService
from .schemas import LicitacionNewResponse
from src.core.responses import ApiResponse

router = APIRouter()

@router.post("/new", response_model=ApiResponse[LicitacionNewResponse])
async def create_licitacion(
    nombre: str = Form(...),
    files: List[UploadFile] = File(...)
):
    return await LicitacionNewService.process(nombre, files)
