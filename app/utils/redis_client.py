from redis import Redis
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Redis连接
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)