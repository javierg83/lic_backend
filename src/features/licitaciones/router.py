from fastapi import APIRouter
from .actions.new.controller import router as new_router

router = APIRouter()

router.include_router(new_router)
