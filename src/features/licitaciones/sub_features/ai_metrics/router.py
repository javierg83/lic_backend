from fastapi import APIRouter
from src.core.responses import ApiResponse
from .schemas import AITokenUsageCreate, AITokenUsageResponse, AIMetricsResponse
from .service import AIMetricsService

router = APIRouter(tags=["AI Metrics"])

@router.post("/{id}/token-usage", response_model=ApiResponse[AITokenUsageResponse])
async def create_token_usage(id: str, data: AITokenUsageCreate):
    return await AIMetricsService.create_log(id, data)

@router.get("/{id}/ai-metrics", response_model=ApiResponse[AIMetricsResponse])
async def get_ai_metrics(id: str):
    return await AIMetricsService.get_metrics(id)
