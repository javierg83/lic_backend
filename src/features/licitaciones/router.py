from fastapi import APIRouter
from .actions.new.controller import router as new_router
from .actions.list.controller import router as list_router

router = APIRouter()

router.include_router(new_router)
router.include_router(list_router)
