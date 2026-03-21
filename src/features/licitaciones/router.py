from fastapi import APIRouter
from .actions.new.controller import router as new_router
from .actions.list.controller import router as list_router
from .actions.show.controller import router as show_router
from .actions.update.controller import router as update_router
from .actions.import_agil.controller import router as import_agil_router
from .sub_features.datos_economicos.router import router as datos_economicos_router
from .sub_features.items.router import router as items_router
from .sub_features.auditoria.router import router as auditoria_router
from .sub_features.homologaciones.router import router as homologaciones_router
from .sub_features.ai_metrics.router import router as ai_metrics_router

router = APIRouter()

router.include_router(new_router)
router.include_router(list_router)
router.include_router(show_router)
router.include_router(update_router)
router.include_router(import_agil_router)
router.include_router(datos_economicos_router)
router.include_router(items_router)
router.include_router(auditoria_router)
router.include_router(homologaciones_router)
router.include_router(ai_metrics_router)
