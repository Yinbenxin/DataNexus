from datetime import datetime
from typing import Dict, Any, Optional
from app.models.file_models import FileModel

class RerankTask(FileModel):
    def __init__(self):
        super().__init__("rerank_task")

    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        file_path = self._get_file_path(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "query": data["query"],
            "texts": data["texts"],
            "top_k": data["top_k"],
            "handle": data.get("handle"),
            "scores": None,
            "rankings": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        fd = self._acquire_lock(file_path)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._serialize(task_data))
            return True
        finally:
            self._release_lock(fd)

# 创建全局实例
rerank_task_model = RerankTask()