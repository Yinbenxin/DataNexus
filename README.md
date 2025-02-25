# ModApp - 数据脱敏和Embedding服务

这是一个基于FastAPI的异步API服务，提供数据脱敏和文本embedding功能。

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

## 安装说明

1. 克隆项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 环境要求

- Python 3.9
- PostgreSQL
- 足够的磁盘空间用于模型存储

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