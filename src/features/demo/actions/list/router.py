from fastapi import APIRouter
from typing import List
from src.core.responses import ApiResponse
from .schemas import DemoListIn, DemoListOut
from .service import DemoListService

router = APIRouter()

@router.post("/list", response_model=ApiResponse[List[DemoListOut]])
async def demo_list(data: DemoListIn):
    return DemoListService.process(data)
