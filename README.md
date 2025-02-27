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
   createdb -O datanexus modapp
   ```

3. 验证数据库连接：
   ```bash
   psql -U datanexus -d modapp
   # 使用 \l 命令查看数据库列表
   # 使用 \q 退出psql
   ```

4. 配置环境变量：
   在项目根目录创建或编辑 `.env` 文件，添加数据库连接信息：
   ```
   DATABASE_URL=postgresql://datanexus:123@localhost:5432/modapp
   ```

5. 创建数据库表结构：
   连接到数据库后，执行以下SQL命令创建必要的表：
   ```sql
   -- 创建mask_tasks表
   CREATE TABLE mask_tasks (
       id SERIAL PRIMARY KEY,
       task_id VARCHAR UNIQUE,
       status VARCHAR,
       original_text TEXT,
       masked_text TEXT,
       mapping JSONB,
       mask_type VARCHAR DEFAULT 'similar',
       mask_model VARCHAR DEFAULT 'paddle',
       mask_field JSONB,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- 创建embedding_tasks表
   CREATE TABLE embedding_tasks (
       id SERIAL PRIMARY KEY,
       task_id VARCHAR UNIQUE,
       status VARCHAR,
       text TEXT,
       embedding JSONB,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

   -- 创建索引
   CREATE INDEX idx_mask_tasks_task_id ON mask_tasks(task_id);
   CREATE INDEX idx_embedding_tasks_task_id ON embedding_tasks(task_id);
   ```

## 环境要求

- Python 3.9
- PostgreSQL
- 足够的磁盘空间用于模型存储

## 安装说明

1. 克隆项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt

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