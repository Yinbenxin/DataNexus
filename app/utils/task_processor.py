import asyncio
import aiohttp
from typing import Dict, Any, Optional, Tuple, Callable, Union, Type
from app.services.embedding_service import EmbeddingService
from app.services.mask_service import MaskService
from app.services.rerank_service import RerankService
from app.utils.queue_manager import task_queue
from app.utils.logger import logger
from app.models import *
import os
class TaskProcessor:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.mask_service = MaskService()
        self.rerank_service = RerankService()
        self.running = False
        # 任务类型到模型的映射
        self.task_models = {
            "embedding": embedding_task_model,
            "mask": mask_task_model,
            "rerank": rerank_task_model
        }

    async def _send_callback(self, 
                           handle: str, 
                           task_id: str, 
                           status: str, 
                           data: Dict[str, Any], 
                           model: Any) -> bool:
        """发送回调结果到指定接口
        
        Args:
            handle: 回调地址
            task_id: 任务ID
            status: 任务状态 (completed/failed)
            data: 回调数据
            model: 任务对应的模型
            
        Returns:
            bool: 回调是否成功
        """
        logger.info(f"返回结果到接口 {handle}")

        if not handle:
            handle = os.getenv("HANDLE_URL")
        if not handle:
            # 如果没有回调地址，直接删除本地任务数据
            logger.info(f"没有回调地址，直接删除本地任务数据 {task_id}")
            await model.delete(task_id)
            return True
        logger.info(f"返回结果到接口 {handle}")
        
        callback_data = {"task_id": task_id, "status": status, **data}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(handle, json=callback_data, timeout=30) as response:
                    if response.status != 200:
                        error_msg = f"返回结果到接口 {handle} 失败: {response.status}"
                        logger.error(error_msg)
                        # 更新本地任务状态为失败
                        # await self._update_task_status(task_id, model, "failed", {
                        #     "error": error_msg,
                        #     **data  # 保留原始数据
                        # })
                        return False
                    # 回调成功后删除本地任务数据
                    logger.info(f"返回结果到接口 {handle} 成功")
                    await model.delete(task_id)
                    return True
        except Exception as e:
            error_msg = f"返回结果到接口 {handle} 时发生错误: {str(e)}"
            logger.error(error_msg)
            # 更新本地任务状态为失败
            # await self._update_task_status(task_id, model, "failed", {
            #     "error": error_msg,
            #     **data  # 保留原始数据
            # })
            return False

    async def _update_task_status(self, 
                               task_id: str, 
                               model: Any, 
                               status: str, 
                               data: Dict[str, Any]) -> None:
        """更新任务状态
        
        Args:
            task_id: 任务ID
            model: 任务对应的模型
            status: 任务状态 (completed/failed)
            data: 更新数据
        """
        update_data = {"status": status, **data}
        await model.update(task_id, update_data)

    async def process_embedding_task(self, task: Dict[str, Any], db: None = None) -> None:
        """处理embedding任务"""
        task_id = task["task_id"]
        model = self.task_models["embedding"]

        # 从任务文件中获取数据
        task_data = await model.get(task_id)
        if not task_data:
            logger.error(f"任务 {task_id} 数据不存在")
            return

        text = task_data["text"]
        handle = task_data.get("handle")

        logger.info(f"开始处理Embedding任务 {task_id}, 文本长度: {len(text)}")

        try:
            # 生成embedding
            embedding = await self.embedding_service.generate_embedding(text)
            await model.delete(task_id)
            
            # 将NumPy数组转换为Python列表
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
            
            logger.info(f"Embedding任务 {task_id} 处理完成")

            # 发送回调
            await self._send_callback(handle, task_id, "completed", {"embedding": embedding}, model)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"处理任务 {task_id} 时发生错误: {error_msg}")
            
            # 发送错误回调
            await self._send_callback(handle, task_id, "failed", {"error": error_msg}, model)

        finally:
            # 标记任务完成
            await task_queue.complete_task(task_id)

    async def process_mask_task(self, task: Dict[str, Any], db: None = None) -> None:
        """处理mask任务"""
        task_id = task["task_id"]
        model = self.task_models["mask"]

        # 从任务文件中获取数据
        task_data = await model.get(task_id)
        if not task_data:
            logger.error(f"任务 {task_id} 数据不存在")
            return

        text = task_data["original_text"]
        mask_type = task_data["mask_type"]
        mask_model = task_data["mask_model"]
        mask_field = task_data["mask_field"]
        force_convert = task_data["force_convert"]
        handle = task_data.get("handle")

        # 记录任务信息
        logger.info(f"开始处理Mask任务 {task_id}, 文本长度: {len(text)}字符, 脱敏类型: {mask_type}, 模型: {mask_model}, handle: {handle}")
        if mask_field:
            logger.info(f"指定脱敏字段: {mask_field}")
        if force_convert:
            logger.info(f"强制转换映射: {force_convert}")

        try:
            # 执行脱敏处理
            masked_text, mapping = await self.mask_service.process_mask(
                text=text,
                mask_type=mask_type,
                mask_model=mask_model,
                mask_field=mask_field,
                force_convert=force_convert
            )
            await model.delete(task_id)
            
            logger.info(f"Mask任务 {task_id} 处理完成")

            # 发送回调
            await self._send_callback(handle, task_id, "completed", {
                "masked_text": masked_text,
                "mapping": mapping
            }, model)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"处理任务 {task_id} 时发生错误: {error_msg}")
            
            # 发送错误回调
            await self._send_callback(handle, task_id, "failed", {"error": error_msg}, model)

        finally:
            # 标记任务完成
            await task_queue.complete_task(task_id)
    
    async def process_rerank_task(self, task: Dict[str, Any], db: None = None) -> None:
        """处理rerank任务"""
        task_id = task["task_id"]
        model = self.task_models["rerank"]

        # 从任务文件中获取数据
        task_data = await model.get(task_id)
        if not task_data:
            logger.error(f"任务 {task_id} 数据不存在")
            return

        query = task_data["query"]
        texts = task_data["texts"]
        top_k = task_data["top_k"]
        handle = task_data.get("handle")

        logger.info(f"开始处理Rerank任务 {task_id}, 查询文本: {query[:50]}, 候选文本数量: {len(texts)}")

        try:
            # 执行重排序
            ranked_pairs = await self.rerank_service.rerank_texts(
                query=query,
                texts=texts,
                top_k=top_k
            )
            await model.delete(task_id)
            
            logger.info(f"Rerank任务 {task_id} 处理完成")

            # 发送回调
            await self._send_callback(handle, task_id, "completed", {"rankings": ranked_pairs}, model)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"处理任务 {task_id} 时发生错误: {error_msg}")
            
            # 发送错误回调
            await self._send_callback(handle, task_id, "failed", {"error": error_msg}, model)

        finally:
            # 标记任务完成
            await task_queue.complete_task(task_id)

    async def start_processing(self):
        """启动任务处理"""
        self.running = True
        while self.running:
            # 获取任务
            task = await task_queue.get_task()
            if task:
                task_type = task["type"]
                if task_type == "embedding":
                    await self.process_embedding_task(task)
                elif task_type == "mask":
                    await self.process_mask_task(task)
                elif task_type == "rerank":
                    await self.process_rerank_task(task)
                else:
                    logger.warning(f"未知任务类型: {task_type}")
            else:
                # 如果没有任务，等待一段时间
                await asyncio.sleep(1)

    def stop_processing(self):
        """停止任务处理"""
        self.running = False

# 创建全局任务处理器实例
task_processor = TaskProcessor()