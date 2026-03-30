from fastapi import APIRouter, File, UploadFile, Form
from uuid import UUID
from typing import List, Optional
from src.core.responses import ApiResponse
from .service import GestionDocumentosService
from .schemas import GestionDocumentoRequest, GestionDocumentoResponse

router = APIRouter()

@router.get("/gestion/{gestion_id}/documentos", response_model=ApiResponse[List[GestionDocumentoResponse]])
async def get_gestion_documentos(gestion_id: UUID):
    return await GestionDocumentosService.process_get(gestion_id)

@router.post("/gestion/{gestion_id}/documentos", response_model=ApiResponse[GestionDocumentoResponse])
async def create_gestion_documento(
    gestion_id: UUID,
    file: UploadFile = File(...),
    tipo_documento: str = Form("OTRO"),
    observacion: Optional[str] = Form(None)
):
    return await GestionDocumentosService.process_post(gestion_id, file, tipo_documento, observacion)

@router.get("/gestion/documentos/{documento_id}/download")
async def download_gestion_documento(documento_id: UUID):
    from fastapi.responses import RedirectResponse
    from fastapi import HTTPException
    
    signed_url = await GestionDocumentosService.process_download(documento_id)
    if not signed_url:
        raise HTTPException(status_code=404, detail="Documento no encontrado o error al generar acceso")
        
    return RedirectResponse(url=signed_url)

@router.delete("/gestion/documentos/{documento_id}")
async def delete_gestion_documento(documento_id: UUID):
    return await GestionDocumentosService.process_delete(documento_id)
