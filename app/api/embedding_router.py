from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from pydantic import BaseModel

from app.models.database import get_db, EmbeddingTask
from app.utils.queue_manager import task_queue
from app.utils.logger import logger

router = APIRouter()

class EmbeddingRequest(BaseModel):
    text: str

@router.post("/", response_model=Dict[str, str])
async def create_embedding_task(
    request: Dict[str, Any],

    db: Session = Depends(get_db)
):
    """创建Embedding任务"""
    text = request["text"]
    task_id = str(uuid.uuid4())
    logger.info(f"开始创建Embedding任务， 创建任务 task_id: {task_id}, text: {text[:10]}，文本长度: {len(text)}")
    
    # 创建任务记录
    task = EmbeddingTask(
        task_id=task_id,
        status="pending",
        text=text
    )
    db.add(task)
    db.commit()
    
    # 添加到任务队列
    success = await task_queue.add_task(
        task_id=task_id,
        task_type="embedding",
        data={"text": text}
    )
    
    if not success:
        task.status = "failed"
        db.commit()
        raise HTTPException(status_code=503, detail="任务队列已满")
    
    return {"task_id": task_id}

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_embedding_task(task_id: str, db: Session = Depends(get_db)):
    """获取Embedding任务状态和结果"""
    task = db.query(EmbeddingTask).filter(EmbeddingTask.task_id == task_id).first()
    if not task:
        return {
            "task_id": None,
            "status": "failed",
            "error": "任务不存在"
        }
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "text": task.text,
        "embedding": task.embedding if task.status == "completed" else None,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

@router.get("/", response_model=Dict[str, int])
async def get_queue_status():
    """获取队列状态"""
    return await task_queue.get_queue_status()