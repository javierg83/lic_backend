from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from src.api.user_auth import auth_required

router = APIRouter()

@router.get("/")
async def main_page():
    return {"message": "hola mundo"}