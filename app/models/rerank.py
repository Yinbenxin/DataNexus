from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from datetime import datetime
from app.models.database import Base

class RerankTask(Base):
    __tablename__ = "rerank_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(String)  # pending, processing, completed, failed
    query = Column(String)
    texts = Column(JSON)  # 候选文本列表
    top_k = Column(Integer)
    scores = Column(JSON)  # 存储相似度得分
    rankings = Column(JSON)  # 存储排序后的文本索引
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)