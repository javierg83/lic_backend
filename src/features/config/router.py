from fastapi import APIRouter, File, UploadFile
from src.core.responses import ApiResponse
from .service import ConfigService

router = APIRouter()

@router.post("/catalogo/upload", response_model=ApiResponse)
async def upload_catalogo(file: UploadFile = File(...)):
    return await ConfigService.upload_catalog(file)
