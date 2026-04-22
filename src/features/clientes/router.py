from fastapi import APIRouter
from .productos.controller import router as productos_router
from .preferencias.controller import router as preferencias_router
from .admin.controller import router as admin_router

router = APIRouter()

# Prefijo lo puede incluir el router principal, aquí incluimos sub-módulos
router.include_router(productos_router, tags=["Clientes"])
router.include_router(preferencias_router, tags=["Clientes"])
router.include_router(admin_router, prefix="/admin", tags=["Admin Clientes"])
