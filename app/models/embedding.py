import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import fcntl
import errno
from .file_models import FileModel

class EmbeddingTask(FileModel):
    def __init__(self):
        super().__init__("embedding_task")
        self.__name__ = "embedding"
    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        file_path = self._get_file_path(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "text": data["text"],
            "embedding": None,
            "handle": data.get("handle", None),  # 获取回调地址
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