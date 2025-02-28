from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

class RerankService:
    def __init__(self, model_name: str = 'TencentBAC/Conan-rerank-v1'):
        """初始化rerank服务

        Args:
            model_name: 使用的模型名称，默认使用TencentBAC/Conan-rerank-v1
        """
        self.model = CrossEncoder(model_name)

    async def rerank(self, query: str, texts: List[str], topk: int = 10) -> List[Dict[str, Any]]:
        """对文本列表进行重排序

        Args:
            query: 查询文本
            texts: 待排序的文本列表
            topk: 返回前k个结果

        Returns:
            排序后的结果列表，每个元素包含文本内容和相关性分数
        """
        # 生成文本对
        text_pairs = [[query, text] for text in texts]
        
        # 计算相关性分数
        scores = self.model.predict(text_pairs)
        
        # 将文本和分数组合
        results = [{
            'text': text,
            'score': float(score)  # 转换为Python float类型以便JSON序列化
        } for text, score in zip(texts, scores)]
        
        # 按分数降序排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前topk个结果
        return results[:topk]