from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import uuid
from pydantic import BaseModel, validator

from app.models import rerank_task_model
from app.utils.queue_manager import task_queue
from app.utils.logger import logger

router = APIRouter()

class RerankRequest(BaseModel):
    query: str
    texts: List[str]
    top_k: int
    handle: str = None

    @validator('query')
    def validate_query(cls, v):
        if not isinstance(v, str):
            raise ValueError('query must be a string')
        return v

    @validator('texts')
    def validate_texts(cls, v):
        if not isinstance(v, list):
            raise ValueError('texts must be a list')
        return v

    @validator('top_k')
    def validate_top_k(cls, v):
        if not isinstance(v, int) or v < 1:
            raise ValueError('top_k must be a positive integer')
        return v

@router.post("/", response_model=Dict[str, Any])
async def create_rerank_task(request: RerankRequest):
    """创建Rerank任务"""
    task_id = str(uuid.uuid4())
    logger.info(f"开始创建Rerank任务，task_id: {task_id}, query: {request.query[:50]}, 候选文本数量: {len(request.texts)}")
    
    # 创建任务记录
    await rerank_task_model.create(task_id, {
        "query": request.query,
        "texts": request.texts,
        "top_k": request.top_k,
        "handle": request.handle
    })
    
    # 添加到任务队列
    success = await task_queue.add_task(
        task_id=task_id,
        task_type="rerank"
    )
    
    if not success:
        await rerank_task_model.update(task_id, {"status": "failed"})
        raise HTTPException(status_code=503, detail="任务队列已满")
    
    return {"task_id": task_id, "success": True}

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_rerank_task(task_id: str):
    """获取Rerank任务状态和结果"""
    task = await rerank_task_model.get(task_id)
    if not task:
        return {
            "task_id": None,
            "status": "failed",
            "error": "任务不存在"
        }
    
    return {
        "task_id": task["task_id"],
        "status": task["status"],
        "query": task["query"],
        "rankings": task["rankings"] if task["status"] == "completed" else None,
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }

@router.get("/", response_model=Dict[str, int])
async def get_queue_status():
    """获取队列状态"""
    return await task_queue.get_queue_status()