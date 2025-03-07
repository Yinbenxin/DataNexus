import json
from datetime import datetime
from typing import Dict, Any, Optional
from redis import Redis
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Redis连接
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

class RedisModel:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def _get_key(self, task_id: str) -> str:
        return f"{self.prefix}:{task_id}"

    def _serialize(self, data: Dict[str, Any]) -> str:
        return json.dumps(data)

    def _deserialize(self, data: str) -> Dict[str, Any]:
        return json.loads(data) if data else {}

    async def delete(self, task_id: str) -> bool:
        """删除任务数据"""
        key = self._get_key(task_id)
        return bool(redis_client.delete(key))

class MaskTask(RedisModel):
    def __init__(self):
        super().__init__("mask_task")

    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        key = self._get_key(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "original_text": data["text"],
            "masked_text": None,
            "mapping": None,
            "mask_type": data.get("mask_type", "similar"),
            "mask_model": data.get("mask_model", "paddle"),
            "mask_field": data.get("mask_field"),
            "force_convert": data.get("force_convert"),
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

class EmbeddingTask(RedisModel):
    def __init__(self):
        super().__init__("embedding_task")

    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        key = self._get_key(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "text": data["text"],
            "embedding": None,
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
mask_task_model = MaskTask()
embedding_task_model = EmbeddingTask()