from fastapi import APIRouter
from .list import demo_list

router = APIRouter()

# Registramos la acción
router.add_api_route("/list", demo_list, methods=["POST"])