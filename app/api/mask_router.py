from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uuid
from app.models.database import get_db, MaskTask
from app.utils.queue_manager import task_queue
from app.services.mask_service import MaskService

router = APIRouter()
mask_service = MaskService()

@router.post("/", response_model=Dict[str, str])
async def create_mask_task(
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """创建脱敏任务"""
    task_id = str(uuid.uuid4())
    
    # 从请求体中获取参数
    text = request["text"]
    mask_type = request.get("mask_type", "similar")
    mask_model = request.get("mask_model", "paddle")
    mask_field = request.get("mask_field", None)
    print("mask_type: ", mask_type)
    print("mask_model: ", mask_model)
    print("mask_field: ", mask_field)
    # 创建任务记录
    task = MaskTask(
        task_id=task_id,
        status="pending",
        original_text=text,
        mask_type=mask_type,
        mask_model=mask_model,
        mask_field=mask_field
    )
    db.add(task)
    db.commit()
    
    # 添加到任务队列
    success = await task_queue.add_task(
        task_id=task_id,
        task_type="mask",
        data={
            "text": text,
            "mask_type": mask_type,
            "mask_model": mask_model,
            "mask_field": mask_field
        }
    )
    
    if not success:
        task.status = "failed"
        db.commit()
        raise HTTPException(status_code=503, detail="任务队列已满")
    
    return {"task_id": task_id}

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_mask_task(task_id: str, db: Session = Depends(get_db)):
    """获取脱敏任务状态和结果"""
    task = db.query(MaskTask).filter(MaskTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "original_text": task.original_text,
        "masked_text": task.masked_text if task.status == "completed" else None,
        "mapping": task.mapping if task.status == "completed" else None,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

@router.get("/", response_model=Dict[str, int])
async def get_queue_status():
    """获取队列状态"""
    return await task_queue.get_queue_status()