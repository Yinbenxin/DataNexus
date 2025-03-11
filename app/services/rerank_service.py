from typing import List, Tuple, Dict, Any
import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
from app.utils.logger import logger


class RerankService:
    def __init__(self):
        #从env中获取模型路径
        logger.info(f"Rerank模型加载中")
        model_name_or_path=os.getenv("RERANK_MODEL_PATH")
        if model_name_or_path=="":
            self.model = None
            self.tokenizer = None
        else:
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name_or_path,
                trust_remote_code=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = model.to(device)
        logger.info(f"Rerank模型加载完成, 模型路径: {model_name_or_path}")

    async def rerank_texts(self, query: str, texts: List[str], top_k: int) -> List[Tuple[str, float]]:
        """对文本进行重排序
        
        Args:
            query: 查询文本
            texts: 待排序的文本列表
            top_k: 返回的top k个结果
        
        Returns:
            Tuple[List[str], List[float]]: 排序后的文本列表和对应的相似度得分
        """
        device = self.model.device
        logger.info(f"正在对查询文本进行重排序: {query[:10]}, 候选文本数量: {len(texts)}")
        logger.info(f"使用设备: {device}")
        pairs = [(query, text) for text in texts]
        scores = []

        # 根据设备动态调整批处理大小
        batch_size = 32 if device.type == "cuda" else 8

        try:
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i:i+batch_size]
                features = self.tokenizer(
                    batch_pairs,
                    padding=True,
                    truncation=True,
                    return_tensors="pt",
                    max_length=512
                )
                features = {k: v.to(device) for k, v in features.items()}

                with torch.no_grad():
                    outputs = self.model(**features)
                    batch_scores = torch.sigmoid(outputs.logits).squeeze(-1).cpu().tolist()
                    scores.extend(batch_scores)

        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logger.info(f"GPU内存不足, 正在尝试减小批处理大小")
                if device.type == "cuda":
                    logger.info(f"正在将模型转移到CPU并重试...")
                    model = self.model.cpu()
                    device = torch.device("cpu")
                    return rerank_texts(query, texts, top_k)
            raise e

        text_score_pairs = list(zip(texts, scores))
        sorted_pairs = sorted(text_score_pairs, key=lambda x: x[1], reverse=True)

        return sorted_pairs[:top_k]
