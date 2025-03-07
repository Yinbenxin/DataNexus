# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖和Redis
RUN apt-get update 
RUN apt-get install -y libgomp1 
RUN apt-get install -y redis-server


# 复制项目文件
COPY requirements.txt /app/

# 更新pip和setuptools，然后安装项目依赖
RUN pip install --no-cache-dir --upgrade pip setuptools>=61.0.0 
RUN pip install --no-cache-dir -r requirements.txt

# 复制其余项目文件
COPY . /app/


# 设置环境变量
ENV REDIS_URL=redis://localhost:6379/0
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4
ENV QUEUE_MAX_SIZE=100
ENV TASK_TIMEOUT=300
ENV TASK_RETENTION_DAYS=30
ENV MODEL_PATH=/app/models
ENV EMBEDDING_MODEL_PATH=/app/models/Conan-embedding-v1
ENV RERANK_MODEL_PATH=/app/models/gte-multilingual-reranker-base
ENV INFO_EXTRACT_MODEL_PATH=/app/models/uie-medium
ENV EMBEDDING_SMELL_ZH=/app/models/bge-small-zh

# 暴露端口
EXPOSE 8000
EXPOSE 6379

# 创建启动脚本
RUN echo '#!/bin/bash\n/etc/init.d/redis-server start\nuvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1' > /app/start.sh \
    && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]
