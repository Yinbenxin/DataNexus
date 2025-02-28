from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rerank_service import RerankService

router = APIRouter()
rerank_service = RerankService()

class RerankRequest(BaseModel):
    query: str
    texts: List[str]
    topk: int = 10

@router.post("/rerank", response_model=List[Dict[str, Any]])
async def rerank_texts(request: RerankRequest):
    """对文本列表进行重排序

    Args:
        request: 包含查询文本、待排序文本列表和topk参数的请求体

    Returns:
        排序后的结果列表，每个元素包含文本内容和相关性分数
    """
    try:
        results = await rerank_service.rerank(
            query=request.query,
            texts=request.texts,
            topk=request.topk
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))