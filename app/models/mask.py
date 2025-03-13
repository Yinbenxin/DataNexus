import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import fcntl
import errno
from .file_models import FileModel

class MaskTask(FileModel):
    def __init__(self):
        super().__init__("mask_task")

    async def create(self, task_id: str, data: Dict[str, Any]) -> bool:
        file_path = self._get_file_path(task_id)
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "original_text": data["text"],
            "masked_text": None,
            "mapping": None,
            "handle": data.get("handle"),
            "mask_type": data.get("mask_type", "similar"),
            "mask_model": data.get("mask_model", "paddle"),
            "mask_field": data.get("mask_field"),
            "force_convert": data.get("force_convert"),
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