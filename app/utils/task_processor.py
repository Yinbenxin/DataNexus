import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.database import EmbeddingTask, MaskTask
from app.models.rerank import RerankTask
from app.services.embedding_service import EmbeddingService
from app.services.mask_service import MaskService
from app.services.rerank_service import RerankService
from app.utils.queue_manager import task_queue
from app.models.database import get_db
from app.utils.logger import logger

class TaskProcessor:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.mask_service = MaskService(embedding_model = self.embedding_service.model)
        self.rerank_service = RerankService()
        self.running = False

    async def process_embedding_task(self, task: Dict[str, Any], db: Session) -> None:
        """处理embedding任务"""
        task_id = task["task_id"]
        text = task["data"]["text"]

        # 更新任务状态为处理中
        db_task = db.query(EmbeddingTask).filter(EmbeddingTask.task_id == task_id).first()
        if db_task:
            db_task.status = "processing"
            db.commit()
            logger.info(f"开始处理任务 {task_id}, 文本长度: {len(text)}")

            try:
                # 生成embedding
                embedding = await self.embedding_service.generate_embedding(text)
                
                # 将NumPy数组转换为Python列表
                if hasattr(embedding, 'tolist'):
                    embedding = embedding.tolist()
                
                # 更新任务状态和结果
                db_task.status = "completed"
                db_task.embedding = embedding
                db.commit()
                logger.info(f"Embedding任务 {task_id} 处理完成")
            except Exception as e:
                # 处理失败，更新状态
                db_task.status = "failed"
                db.commit()
                logger.info(f"处理任务 {task_id} 时发生错误: {str(e)}")

        # 标记任务完成
        await task_queue.complete_task(task_id)

    async def process_mask_task(self, task: Dict[str, Any], db: Session) -> None:
        """处理mask任务"""
        task_id = task["task_id"]
        text = task["data"]["text"]
        mask_type = task["data"]["mask_type"]
        mask_model = task["data"]["mask_model"]
        mask_field = task["data"]["mask_field"]
        force_convert = task["data"]["force_convert"]

        # 更新任务状态为处理中
        db_task = db.query(MaskTask).filter(MaskTask.task_id == task_id).first()
        if db_task:
            db_task.status = "processing"
            db.commit()
            logger.info(f"开始处理Mask任务 {task_id}, 文本长度: {len(text)}字符, 脱敏类型: {mask_type}, 模型: {mask_model}")
            if mask_field:
                logger.info(f"指定脱敏字段: {mask_field}")
            if force_convert:
                logger.info(f"强制转换映射: {force_convert}")
            logger.info(f"开始处理Embedding任务 {task_id}, 文本长度: {len(text)}字符")

            try:
                # 执行脱敏处理
                masked_text, mapping = await self.mask_service.process_mask(
                    text=text,
                    mask_type=mask_type,
                    mask_model=mask_model,
                    mask_field=mask_field,
                    force_convert=force_convert
                )
                
                # 更新任务状态和结果
                db_task.status = "completed"
                db_task.masked_text = masked_text
                db_task.mapping = mapping
                db.commit()
                logger.info(f"Mask任务 {task_id} 处理完成")
            except Exception as e:
                # 处理失败，更新状态
                db_task.status = "failed"
                db_task.masked_text = str(e)
                
                db.commit()
                logger.info(f"处理任务 {task_id} 时发生错误: {str(e)}")

        # 标记任务完成
        await task_queue.complete_task(task_id)

    async def start_processing(self):
        """启动任务处理"""
        self.running = True
        while self.running:
            # 获取任务
            task = await task_queue.get_task()
            if task:
                # 获取数据库会话
                db = next(get_db())
                try:
                    if task["type"] == "embedding":
                        await self.process_embedding_task(task, db)
                    elif task["type"] == "mask":
                        await self.process_mask_task(task, db)
                    elif task["type"] == "rerank":
                        await self.process_rerank_task(task, db)
                finally:
                    db.close()
            else:
                # 如果没有任务，等待一段时间
                await asyncio.sleep(1)

    async def process_rerank_task(self, task: Dict[str, Any], db: Session) -> None:
        """处理rerank任务"""
        task_id = task["task_id"]
        query = task["data"]["query"]
        texts = task["data"]["texts"]
        top_k = task["data"]["top_k"]

        # 更新任务状态为处理中
        db_task = db.query(RerankTask).filter(RerankTask.task_id == task_id).first()
        if db_task:
            db_task.status = "processing"
            db.commit()
            logger.info(f"开始处理Rerank任务 {task_id}, 查询文本: {query[:50]}, 候选文本数量: {len(texts)}")

            try:
                # 执行重排序
                ranked_pairs = await self.rerank_service.rerank_texts(
                    query=query,
                    texts=texts,
                    top_k=top_k
                )
                
                # 更新任务状态和结果
                db_task.status = "completed"
                db_task.rankings = ranked_pairs  # 直接存储元组列表
                db.commit()
                logger.info(f"Rerank任务 {task_id} 处理完成")
            except Exception as e:
                # 处理失败，更新状态
                db_task.status = "failed"
                db.commit()
                logger.info(f"处理任务 {task_id} 时发生错误: {str(e)}")

        # 标记任务完成
        await task_queue.complete_task(task_id)

    def stop_processing(self):
        """停止任务处理"""
        self.running = False

# 创建全局任务处理器实例
task_processor = TaskProcessor()