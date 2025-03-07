from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import uuid
from app.models.redis_models import mask_task_model
from app.utils.queue_manager import task_queue
from app.services.mask_service import MaskService
from app.utils.logger import logger

router = APIRouter()
mask_service = MaskService()

@router.post("/", response_model=Dict[str, str])
async def create_mask_task(request: Dict[str, Any]):
    """创建脱敏任务"""
    task_id = str(uuid.uuid4())
    
    # 从请求体中获取参数
    text = request["text"]
    mask_type = request.get("mask_type", "similar")
    mask_model = request.get("mask_model", "paddle")
    mask_field = request.get("mask_field", None)
    force_convert = request.get("force_convert", None)
    
    try:
        # 记录请求信息
        logger.info(f"Received request: {request}, task_id: {task_id}, text: {text[:20]}..., mask_type: {mask_type}, mask_model: {mask_model}, mask_field: {mask_field}, force_convert: {force_convert}")
        
        # 创建任务记录
        success = await mask_task_model.create(task_id, {
            "text": text,
            "mask_type": mask_type,
            "mask_model": mask_model,
            "mask_field": mask_field,
            "force_convert": force_convert
        })
        
        if not success:
            logger.error(f"Failed to create task record in Redis for task_id: {task_id}")
            raise HTTPException(status_code=500, detail="Failed to create task record")
        
        # 添加到任务队列
        success = await task_queue.add_task(
            task_id=task_id,
            task_type="mask",
            data={
                "text": text,
                "mask_type": mask_type,
                "mask_model": mask_model,
                "mask_field": mask_field,
                "force_convert": force_convert
            }
        )
        
        if not success:
            logger.error(f"Task queue is full, failed to add task_id: {task_id}")
            await mask_task_model.update(task_id, {"status": "failed", "masked_text": "任务队列已满"})
            raise HTTPException(status_code=503, detail="任务队列已满")
        
        return {"task_id": task_id}
    except Exception as e:
        # 如果在创建过程中发生任何错误，更新任务状态为失败
        error_message = str(e)
        logger.error(f"Error occurred while creating task {task_id}: {error_message}")
        try:
            await mask_task_model.update(task_id, {"status": "failed", "masked_text": error_message})
        except Exception as update_error:
            logger.error(f"Failed to update task status for {task_id}: {str(update_error)}")
        raise HTTPException(status_code=500, detail=error_message)

@router.get("/{task_id}", response_model=Dict[str, Any])
async def get_mask_task(task_id: str):
    """获取脱敏任务状态和结果"""
    task = await mask_task_model.get(task_id)
    if not task:
        return {
            "task_id": None,
            "status": "failed",
            "error": "任务不存在",
            "original_text": None
        }
    
    response = {
        "task_id": task["task_id"],
        "status": task["status"],
        "original_text": task["original_text"],
        "masked_text": task["masked_text"] if task["status"] == "completed" else None,
        "mapping": task["mapping"] if task["status"] == "completed" else None,
        "created_at": task["created_at"],
        "updated_at": task["updated_at"]
    }
    
    # 如果任务失败，添加错误信息
    if task["status"] == "failed":
        response["error"] = task["masked_text"]
        response["masked_text"] = ""
    
    return response

@router.get("/", response_model=Dict[str, int])
async def get_queue_status():
    """获取队列状态"""
    return await task_queue.get_queue_status()