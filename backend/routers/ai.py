from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ml.models.baseline import BaselineModel

router = APIRouter()
model = BaselineModel()

# --- Схемы запросов/ответов (по контракту из лабы 2) ---
class SummarizeRequest(BaseModel):
    game_id: str
    store_text: str

class SummarizeResponse(BaseModel):
    game_id: str
    narrative: str

class ClassifyRequest(BaseModel):
    game_id: str
    metrics_4w: List[float]

class ClassifyResponse(BaseModel):
    game_id: str
    category: str

# --- Эндпоинты ---
@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        result = model.summarize(request.game_id, request.store_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify", response_model=ClassifyResponse)
async def classify(request: ClassifyRequest):
    try:
        result = model.classify(request.game_id, request.metrics_4w)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "ok"}
