from asyncio import Queue, Lock
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()

class TaskQueue:
    def __init__(self):
        self.queue = Queue(maxsize=int(os.getenv("QUEUE_MAX_SIZE", 100)))
        self.processing: Dict[str, Any] = {}
        self.lock = Lock()

    async def add_task(self, task_id: str, task_type: str, data: Dict[str, Any]) -> bool:
        """添加任务到队列"""
        if self.queue.full():
            return False
        
        task_data = {
            "task_id": task_id,
            "type": task_type,
            "data": data
        }
        await self.queue.put(task_data)
        logger.info(f"添加任务到队列: {task_id}, 类型: {task_type}")
        return True

    async def get_task(self) -> Optional[Dict[str, Any]]:
        """从队列获取任务"""
        if self.queue.empty():
            return None
        
        task = await self.queue.get()
        async with self.lock:
            self.processing[task["task_id"]] = task
        logger.info(f"从队列获取任务: {task['task_id']}, 任务类型: {task['type']}")
        return task

    async def complete_task(self, task_id: str) -> None:
        """完成任务处理"""
        async with self.lock:
            if task_id in self.processing:
                del self.processing[task_id]
                logger.info(f"完成任务处理: {task_id}")

    async def get_queue_status(self) -> Dict[str, int]:
        """获取队列状态"""
        return {
            "waiting": self.queue.qsize(),
            "processing": len(self.processing)
        }

# 创建全局任务队列实例
task_queue = TaskQueue()