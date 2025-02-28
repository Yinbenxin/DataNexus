from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import time


class EmbeddingService:
    def __init__(self, embedding_model=None):
        # 初始化模型，使用多语言BERT模型
        # self.model = 12345
        if embedding_model:
            self.model = embedding_model
        else:
            self.model = SentenceTransformer('TencentBAC/Conan-embedding-v1')
    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量"""
        embeddings = self.model.encode([text])
        return embeddings.tolist()[0]