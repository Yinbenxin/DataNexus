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
- Alibaba-NLP/gte-multilingual-reranker-base
- PaddlePaddle/uie-medium
- BAAI/bge-small-zh


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
   git clone https://huggingface.co/PaddlePaddle/uie-medium ${MODEL_PATH}
   git clone https://huggingface.co/BAAI/bge-small-zh ${MODEL_PATH}
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

启动服务后访问：`http://localhost:8000/`

### API调用方式

本服务支持两种API调用方式：同步调用和异步回调。

#### 1. 同步调用

同步调用方式通过轮询获取任务结果：

1. 创建任务：
```python
import requests

# 创建Embedding任务
response = requests.post(
    "http://localhost:8000/api/v1/embedding",
    json={"text": "需要处理的文本"}
)

task_id = response.json()["task_id"]
```

2. 轮询获取结果：
```python
import time

while True:
    # 查询任务状态
    response = requests.get(f"http://localhost:8000/api/v1/embedding/{task_id}")
    result = response.json()
    
    if result["status"] == "completed":
        # 处理成功的结果
        embedding = result["embedding"]
        break
    elif result["status"] == "failed":
        # 处理失败
        error = result.get("error")
        break
    
    # 等待一段时间后继续查询
    time.sleep(1)
```

#### 2. 异步回调

异步回调方式通过提供回调地址自动接收结果：

1. 创建任务时提供回调地址：
```python
import requests

# 创建Embedding任务
response = requests.post(
    "http://localhost:8000/api/v1/embedding",
    json={
        "text": "需要处理的文本",
        "handle": "http://your-callback-url/api/callback"
    }
)

task_id = response.json()["task_id"]
```

2. 实现回调接口：
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/api/callback")
async def callback(request: Request):
    result = await request.json()
    
    if result["status"] == "completed":
        # 处理成功的结果
        task_id = result["task_id"]
        embedding = result["embedding"]
    else:
        # 处理失败
        error = result.get("error")
    
    return {"status": "ok"}
```

回调结果格式：
```json
{
    "task_id": "任务ID",
    "status": "completed",  # 或 "failed"
    "embedding": [...],     # 处理成功时返回
    "error": "错误信息"     # 处理失败时返回
}
```

注意事项：
- 回调接口需要返回HTTP状态码200表示成功接收
- 建议实现回调接口的幂等性，防止重复处理
- 回调超时或失败可能会重试