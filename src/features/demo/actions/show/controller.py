from fastapi import APIRouter
from src.core.responses import ApiResponse
from .schemas import DemoShowIn, DemoShowOut
from .service import DemoShowService

router = APIRouter()

@router.post("/show", response_model=ApiResponse[DemoShowOut])
async def demo_show(data: DemoShowIn):
    return DemoShowService.process(data)
