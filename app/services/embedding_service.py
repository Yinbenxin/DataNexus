from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

import torch
import time
from app.utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self, embedding_model=None):
        try:
            logger.info(f"Embedding模型加载开始, 模型: TencentBAC/Conan-embedding-v1")
            # 加载分词器和模型
            try:
                self.model = SentenceTransformer("TencentBAC/Conan-embedding-v1", local_files_only=True)
                logger.info(f"本地模型加载成功，self.model：{self.model}")
                
            except:
                self.model = SentenceTransformer("TencentBAC/Conan-embedding-v1")
                logger.info(f"联网加载模型成功")

            if self.model is None:
                self.model = SentenceTransformer("TencentBAC/Conan-embedding-v1")
                
            if self.model is None:
                raise Exception("Embedding模型加载失败")
            # 将模型设置为评估模式
            self.model.eval()
            logger.info(f"Embedding模型加载完成, 模型: TencentBAC/Conan-embedding-v1")
        except Exception as e:
            logger.error(f"Embedding模型加载失败: {str(e)}")
            raise Exception(f"Embedding模型加载失败: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量"""
        logger.info(f"Embedding文本: {len(text)}")
        embeddings = self.model.encode([text])
        return embeddings.tolist()[0]