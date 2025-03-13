# 使用Python 3.9作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free" > /etc/apt/sources.list
RUN echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main contrib non-free" >> /etc/apt/sources.list
RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list
RUN apt-get update 
RUN apt-get install -y libgomp1 
RUN apt-get install -y libgl1-mesa-glx 
RUN apt-get install -y libglib2.0-0
RUN apt-get install -y poppler-utils
RUN rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt /app/

# 更新pip和setuptools，然后安装项目依赖
RUN pip install --no-cache-dir --upgrade pip setuptools==61.0.0 
RUN pip install --no-cache-dir -r requirements.txt

# 复制其余项目文件
COPY . /app/


# 暴露端口
EXPOSE 8000

# 创建启动脚本
RUN echo '#!/bin/bash\nuvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1' > /app/start.sh \
    && chmod +x /app/start.sh

# 启动命令
CMD ["/app/start.sh"]
