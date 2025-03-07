from datetime import datetime
from typing import Dict, Any, Optional
from app.utils.redis_client import redis_client
from app.models.redis_models import RedisModel

class RerankTask(RedisModel):
    def __init__(self):
        super().__init__("rerank_task")

    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        key = self._get_key(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "query": data["query"],
            "texts": data["texts"],
            "top_k": data["top_k"],
            "scores": None,
            "rankings": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        return redis_client.set(key, self._serialize(task_data))

    async def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        key = self._get_key(task_id)
        data = redis_client.get(key)
        return self._deserialize(data) if data else None

    async def update(self, task_id: str, updates: Dict[str, Any]) -> bool:
        key = self._get_key(task_id)
        data = redis_client.get(key)
        if data:
            task_data = self._deserialize(data)
            task_data.update(updates)
            task_data["updated_at"] = datetime.utcnow().isoformat()
            return redis_client.set(key, self._serialize(task_data))
        return False

# 创建全局实例
rerank_task_model = RerankTask()