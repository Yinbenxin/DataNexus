from .embedding import EmbeddingTask
from .mask import MaskTask
from .rerank import RerankTask

# 创建全局实例
embedding_task_model = EmbeddingTask()
mask_task_model = MaskTask()
rerank_task_model = RerankTask()