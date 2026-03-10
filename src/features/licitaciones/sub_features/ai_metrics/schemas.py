from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AITokenUsageCreate(BaseModel):
    action: str = Field(..., description="Action or stage: e.g. EXTRACCION_TEXTO_OCR")
    provider: str = Field(..., description="Provider name: e.g. openai")
    model: str = Field(..., description="Model name: e.g. gpt-4o")
    input_tokens: int = Field(0, description="Number of prompt tokens")
    output_tokens: int = Field(0, description="Number of completion tokens")

class AITokenUsageResponse(BaseModel):
    id: int
    licitacion_id: str
    action: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    created_at: datetime

    class Config:
        from_attributes = True

class AIMetricsSummary(BaseModel):
    action: str
    provider: str
    model: str
    total_input: int
    total_output: int
    total_tokens: int

class AIMetricsResponse(BaseModel):
    licitacion_id: str
    logs: List[AITokenUsageResponse]
    summary: List[AIMetricsSummary]
    total_input_all: int
    total_output_all: int
    total_all: int
