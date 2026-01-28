from fastapi import APIRouter
from .actions.new.controller import router as new_router
from .actions.list.controller import router as list_router
from .actions.show.controller import router as show_router
from .actions.update.controller import router as update_router
from .sub_features.datos_economicos.router import router as datos_economicos_router
from .sub_features.items.router import router as items_router

router = APIRouter()

router.include_router(new_router)
router.include_router(list_router)
router.include_router(show_router)
router.include_router(update_router)
router.include_router(datos_economicos_router)
router.include_router(items_router)
