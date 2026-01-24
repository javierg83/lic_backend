from fastapi import APIRouter
from .actions.show.controller import router as show_router
from .actions.list.controller import router as list_router
from .actions.new.controller import router as new_router

router = APIRouter()

router.include_router(show_router)
router.include_router(list_router)
router.include_router(new_router)
