from fastapi import APIRouter
from .actions.new.controller import router as new_router
from .actions.list.controller import router as list_router
from .actions.show.controller import router as show_router
from .sub_features.datos_economicos.router import router as datos_economicos_router

router = APIRouter()

router.include_router(new_router)
router.include_router(list_router)
router.include_router(show_router)
router.include_router(datos_economicos_router)
