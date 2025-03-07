from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import asyncio
from app.utils.task_processor import task_processor
from app.models.redis_models import redis_client

# 加载环境变量
load_dotenv()

# 创建FastAPI应用实例
app = FastAPI(
    title="nexusdata API",
    description="数据脱敏和Embedding服务API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # 启动任务处理器
    asyncio.create_task(task_processor.start_processing())
    
    # 启动定时清理任务
    async def schedule_cleanup():
        while True:
            await asyncio.sleep(24 * 60 * 60)  # 每24小时执行一次
            # 获取过期时间（天数）
            retention_days = int(os.getenv("TASK_RETENTION_DAYS", 30))
            # 清理过期的任务数据
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
    
    asyncio.create_task(schedule_cleanup())

@app.on_event("shutdown")
def shutdown_event():
    # 停止任务处理器
    task_processor.stop_processing()

# 导入路由
from app.api.mask_router import router as mask_router
from app.api.embedding_router import router as embedding_router
from app.api.rerank_router import router as rerank_router

# 注册路由
app.include_router(mask_router, prefix="/api/v1/mask", tags=["mask"])
app.include_router(embedding_router, prefix="/api/v1/embedding", tags=["embedding"])
app.include_router(rerank_router, prefix="/api/v1/rerank", tags=["rerank"])

@app.get("/ping")
async def ping():
    return "pong"

@app.get("/")
async def root():
    return {"message": "欢迎使用nexusdata API服务"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )