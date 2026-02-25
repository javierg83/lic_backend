from fastapi import APIRouter
from .actions.list.controller import router as list_router

router = APIRouter()
router.include_router(list_router)
