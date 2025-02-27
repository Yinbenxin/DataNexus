from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models.database import get_db, MaskTask, EmbeddingTask
import os
from dotenv import load_dotenv
from app.utils.logger import logger

# 加载环境变量
load_dotenv()


async def clean_expired_tasks():
    """清理一个月前的任务记录"""
    try:
        # 从环境变量获取任务保留天数，默认为30天
        retention_days = int(os.getenv("TASK_RETENTION_DAYS", 30))
        # 计算过期时间
        expired_time = datetime.utcnow() - timedelta(days=retention_days)
        
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 删除过期的脱敏任务
            mask_result = db.query(MaskTask).filter(
                MaskTask.created_at < expired_time
            ).delete()
            
            # 删除过期的Embedding任务
            embedding_result = db.query(EmbeddingTask).filter(
                EmbeddingTask.created_at < expired_time
            ).delete()
            
            # 提交事务
            db.commit()
            
            logger.info(f"成功清理过期任务：{mask_result} 个脱敏任务，{embedding_result} 个Embedding任务")
            
        except Exception as e:
            db.rollback()
            logger.error(f"清理过期任务时发生错误：{str(e)}")
            raise
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"执行清理任务时发生错误：{str(e)}")
        raise