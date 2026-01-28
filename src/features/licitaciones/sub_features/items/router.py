from fastapi import APIRouter
from .actions.show.controller import router as show_router

router = APIRouter()

router.include_router(show_router)
