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
  - Redis持久化

## 环境要求

- Python 3.9
- Redis
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
3. 模型说明：
   ```bash
     #所有模型会在启动时自动下载到本地
     https://huggingface.co/TencentBAC/Conan-embedding-v1
     https://huggingface.co/Alibaba-NLP/gte-multilingual-reranker-base 
     https://huggingface.co/PaddlePaddle/uie-medium 
     https://huggingface.co/BAAI/bge-small-zh 
   ```

## 启动服务

```bash
uvicorn app.main:app --reload
```

## API文档

启动服务后访问：`http://localhost:8000/docs`

### API调用方式

本服务支持两种API调用方式：同步调用和异步回调。

#### 1. 数据脱敏接口

##### 请求地址
`POST /api/v1/mask`

##### 请求参数
```json
{
    "text": "待脱敏文本",
    "mask_type": "脱敏类型",  // similar, type_replace, delete, aes, md5, sha256, asterisk
    "mask_model": "paddle",  // 使用的模型，目前支持paddle
    "mask_field": ["日期", "姓名", "职业", "地区", "外国人名"],  // 需要脱敏的字段
    "handle": "回调地址"  // 可选，异步回调时使用
}
```

##### 响应格式
```json
{
    "task_id": "任务ID",
    "success": true
}
```

##### 回调数据格式
```json
{
    "task_id": "任务ID",
    "status": "completed",
    "masked_text": "脱敏后的文本",
    "mapping": {"原文": "脱敏后的文本"}
}
```

#### 2. Embedding接口

##### 请求地址
`POST /api/v1/embedding`

##### 请求参数
```json
{
    "text": "待处理文本",
    "handle": "回调地址"  // 可选，异步回调时使用
}
```

##### 响应格式
```json
{
    "task_id": "任务ID",
    "success": true
}
```

##### 回调数据格式
```json
{
    "task_id": "任务ID",
    "status": "completed",
    "embedding": [0.1, 0.2, ...],  // 向量数组
    "text": "原始文本"
}
```

#### 3. Rerank接口

##### 请求地址
`POST /api/v1/rerank`

##### 请求参数
```json
{
    "query": "查询文本",
    "texts": ["候选文本1", "候选文本2", ...],
    "top_k": 3,  // 可选，返回前k个结果
    "handle": "回调地址"  // 可选，异步回调时使用
}
```

##### 响应格式
```json
{
    "task_id": "任务ID",
    "success": true
}
```

##### 回调数据格式
```json
{
    "task_id": "任务ID",
    "status": "completed",
    "rankings": [
        ["最相关文本", 0.95],
        ["次相关文本", 0.85],
        ...
    ]
}
```

#### 4. 同步调用示例

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
        "handle": "http://your-callback-url"
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