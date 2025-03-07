from datetime import datetime
import json
import os
from dotenv import load_dotenv
from app.models.redis_models import redis_client

# 加载环境变量
load_dotenv()

async def clean_expired_tasks():
    """清理过期的任务数据"""
    try:
        # 获取过期时间（天数）
        retention_days = int(os.getenv("TASK_RETENTION_DAYS", 30))
        
        # 获取所有任务的键
        keys = redis_client.keys("*_task:*")
        for key in keys:
            task_data = redis_client.get(key)
            if task_data:
                try:
                    task = json.loads(task_data)
                    created_at = datetime.fromisoformat(task["created_at"])
                    if (datetime.utcnow() - created_at).days > retention_days:
                        redis_client.delete(key)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    except Exception as e:
        print(f"清理过期任务时发生错误: {str(e)}")