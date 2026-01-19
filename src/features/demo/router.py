from fastapi import APIRouter
from .actions.show.router import router as show_router
from .actions.list.router import router as list_router
from .actions.new.router import router as new_router

router = APIRouter()

router.include_router(show_router)
router.include_router(list_router)
router.include_router(new_router)
