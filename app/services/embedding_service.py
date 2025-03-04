from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import time
from dotenv import load_dotenv
from app.utils.logger import logger
import os
load_dotenv()

class EmbeddingService:
    def __init__(self, embedding_model=None):
        # 初始化模型，使用多语言BERT模型
        logger.info(f"Embedding模型加载中")

        model_name_or_path=os.getenv("EMBEDDING_MODEL_PATH")

        if model_name_or_path=="":
            model_name_or_path = 'TencentBAC/Conan-embedding-v1'
        self.model = SentenceTransformer('TencentBAC/Conan-embedding-v1')
        logger.info(f"Embedding模型加载完成, 模型路径: {model_name_or_path}")

    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量"""
        logger.info(f"Embedding文本: {text[:50]}")
        embeddings = self.model.encode([text])
        return embeddings.tolist()[0]