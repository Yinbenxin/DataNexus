from typing import List
import numpy as np
from transformers import AutoModel, AutoTokenizer
import torch
import time
from app.utils.logger import logger
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self, embedding_model=None):
        try:
            model_name_or_path = os.getenv("EMBEDDING_MODEL_PATH")
            if not model_name_or_path:
                model_name_or_path = 'TencentBAC/Conan-embedding-v1'
                logger.info(f"未设置EMBEDDING_MODEL_PATH环境变量，使用默认模型: {model_name_or_path}")
            else:
                logger.info(f"Embedding模型加载中, 模型路径: {model_name_or_path}")
                if not os.path.exists(model_name_or_path):
                    logger.warning(f"指定的模型路径不存在: {model_name_or_path}，将使用默认模型")
                    model_name_or_path = 'TencentBAC/Conan-embedding-v1'
            
            # 加载分词器和模型
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
            self.model = AutoModel.from_pretrained(model_name_or_path)
            # 将模型设置为评估模式
            self.model.eval()
            logger.info(f"Embedding模型加载完成, 模型路径: {model_name_or_path}")
        except Exception as e:
            logger.error(f"Embedding模型加载失败: {str(e)}")
            raise Exception(f"Embedding模型加载失败: {str(e)}")

    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的embedding向量"""
        logger.info(f"Embedding文本: {text[:50]}")
        try:
            # 对文本进行编码
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # 使用模型生成embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                # 使用最后一层隐藏状态的平均值作为文本的embedding
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # 转换为列表格式
            return embeddings[0].tolist()
        except Exception as e:
            logger.error(f"生成Embedding失败: {str(e)}")
            raise Exception(f"生成Embedding失败: {str(e)}")