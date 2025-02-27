# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 安装PostgreSQL客户端和其他必要工具
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV DATABASE_URL=postgresql://datanexus:123@localhost:5432/modapp
ENV MODEL_DIR=./models
ENV MASK_MODEL_PATH=./models/mask
ENV EMBEDDING_MODEL_PATH=./models/embedding
ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4
ENV QUEUE_MAX_SIZE=100
ENV TASK_TIMEOUT=300
ENV TASK_RETENTION_DAYS=30

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]