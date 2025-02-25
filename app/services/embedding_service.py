from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import time

class EmbeddingService:
    def __init__(self):
        # 初始化模型，使用多语言BERT模型
        # self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.model  = 123
    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量"""
        # sleep 20s
        time.sleep(20)
        return [0.1, 0.2, 0.3]