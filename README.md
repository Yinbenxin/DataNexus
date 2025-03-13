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

## 环境要求

- Python 3.9
- 足够的磁盘空间用于模型存储

## 模型要求

- TencentBAC/Conan-embedding-v1
- Alibaba-NLP/gte-multilingual-reranker-base
- PaddlePaddle/uie-medium
- BAAI/bge-small-zh
- OCR

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

调用实例见 tests/test_mask.py
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

调用实例见 tests/test_embedding.py
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

调用实例见 tests/test_rerank.py
```

#### 4. OCR接口

##### 图片文本提取

###### 请求地址
`POST /api/v1/ocr/image`

###### 请求格式
- Content-Type: application/octet-stream
- 请求体：图片的二进制数据

###### 响应格式
```json
{
    "result": "提取的文本内容"
}
```

##### PDF文本提取

###### 请求地址
`POST /api/v1/ocr/pdf`

###### 请求参数
```json
{
    "pdf_url": "PDF文件的URL地址",
    "page": 0  // 可选，指定页码，-1表示提取所有页面
}
```

###### 响应格式
```json
{
    "result": "提取的文本内容"
}
```

###### 错误响应
```json
{
    "detail": "错误信息描述"
}
```

调用实例见 tests/test_ocr.py
```

