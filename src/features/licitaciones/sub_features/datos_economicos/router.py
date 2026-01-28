from fastapi import APIRouter
from .actions.show.controller import router as show_router
from .actions.update.controller import router as update_router

router = APIRouter()

router.include_router(show_router)
router.include_router(update_router)
