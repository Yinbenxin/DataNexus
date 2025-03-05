from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建数据库引擎
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
# 创建基类
Base = declarative_base()

class MaskTask(Base):
    __tablename__ = "mask_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(String)  # pending, processing, completed, failed
    original_text = Column(String)
    masked_text = Column(String)
    mapping = Column(JSON)  # 存储脱敏映射关系
    mask_type = Column(String, default="similar")  # 脱敏类型，如text、image等
    mask_model = Column(String, default="paddle")  # 脱敏模型类型
    mask_field = Column(JSON)  # 需要脱敏的字段列表
    force_convert = Column(JSON)  # 强制转换的映射关系，格式：[[str1,str2],[str1,str2],...]，默认为空
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmbeddingTask(Base):
    __tablename__ = "embedding_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    status = Column(String)  # pending, processing, completed, failed
    text = Column(String)
    embedding = Column(JSON)  # 存储embedding结果
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()