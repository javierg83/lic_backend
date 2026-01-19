from fastapi import APIRouter
from src.core.responses import ApiResponse
from .schemas import DemoNewIn, DemoNewOut
from .service import DemoNewService

router = APIRouter()

@router.post("/new", response_model=ApiResponse[DemoNewOut])
async def demo_new(data: DemoNewIn):
    print(data)
    return DemoNewService.process(data)
