## DataNexus - 数据脱敏、Embedding、rarank服务

这是一个基于FastAPI的异步API服务，提供数据脱敏、文本embedding和rarank功能。

## 功能特点

- 数据脱敏服务
  - 支持文本数据脱敏
  - 自动保存脱敏映射关系
  - 任务追踪和历史记录

- Embedding服务
  - 文本向量化
  - 高性能异步处理

- 通用特性
  - 异步API设计
  - 任务队列支持
  - 数据库持久化

### 数据库初始化

1. 创建数据库用户：
   ```bash
   createuser -P datanexus
   # 根据提示输入密码（示例使用：123）
   ```

2. 创建应用数据库：
   ```bash
   createdb -O datanexus nexusdata
   ```

3. 验证数据库连接：
   ```bash
   psql -U datanexus -d nexusdata
   # 使用 \l 命令查看数据库列表
   # 使用 \q 退出psql
   ```

## 环境要求

- Python 3.9
- PostgreSQL
- 足够的磁盘空间用于模型存储

## 模型要求

- TencentBAC/Conan-embedding-v1
- gte-multilingual-reranker-base
- 足够的磁盘空间用于模型存储


## 安装说明

1. 克隆项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 模型下载：
   ```bash
   export MODEL_PATH=./models
   git clone https://huggingface.co/TencentBAC/Conan-embedding-v1 ${MODEL_PATH}
   git clone https://huggingface.co/Alibaba-NLP/gte-multilingual-reranker-base ${MODEL_PATH}
   git clone git clone https://huggingface.co/PaddlePaddle/uie-medium ${MODEL_PATH}
   ```
## 配置说明

1. 创建`.env`文件并设置必要的环境变量
2. 确保数据库已正确配置
3. 下载并放置必要的模型文件

## 启动服务

```bash
uvicorn app.main:app --reload
```

## API文档

启动服务后访问：`http://localhost:8000/docs`