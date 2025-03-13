import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import fcntl
import errno

class FileModel:
    def __init__(self, prefix: str):
        self.prefix = prefix
        self.data_dir = Path(os.getenv("DATA_DIR", "data/tasks"))
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, task_id: str) -> Path:
        return self.data_dir / f"{task_id}.json"

    def _serialize(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _deserialize(self, data: str) -> Dict[str, Any]:
        return json.loads(data) if data else {}

    def _acquire_lock(self, file_path: Path):
        """获取文件锁"""
        try:
            fd = os.open(str(file_path), os.O_RDWR | os.O_CREAT)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except OSError as e:
            if e.errno == errno.EACCES:
                return None
            raise

    def _release_lock(self, fd):
        """释放文件锁"""
        if fd is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    async def delete(self, task_id: str) -> bool:
        """删除任务数据"""
        file_path = self._get_file_path(task_id)
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    async def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_file_path(task_id)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return self._deserialize(f.read())
        except FileNotFoundError:
            return None

    async def update(self, task_id: str, updates: Dict[str, Any]) -> bool:
        file_path = self._get_file_path(task_id)
        if not file_path.exists():
            return False

        fd = self._acquire_lock(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                task_data = self._deserialize(f.read())
            
            task_data.update(updates)
            task_data["updated_at"] = datetime.utcnow().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._serialize(task_data))
            return True
        finally:
            self._release_lock(fd)