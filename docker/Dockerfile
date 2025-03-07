# 使用Python 3.9作为基础镜像
FROM  python:3.9-slim 

# 设置工作目录
WORKDIR /app

# 安装系统依赖和PostgreSQL
RUN for i in $(seq 1 10); do \
      apt-get update && apt-get install -y \
        postgresql \
        postgresql-contrib \
        && rm -rf /var/lib/apt/lists/* && break \
      || { echo "Attempt $i failed! Retrying in 5 seconds..."; sleep 0.1; }; \
    done

# 复制项目文件
COPY . /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置PostgreSQL
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER datanexus WITH SUPERUSER PASSWORD '123';" && \
    createdb -O datanexus nexusdata 

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=postgresql://datanexus:123@localhost:5432/nexusdata

# 暴露端口
EXPOSE 8000 5432

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
