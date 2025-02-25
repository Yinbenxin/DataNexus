import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建logs目录
logs_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'logs'
logs_dir.mkdir(exist_ok=True)

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """设置日志记录器"""
    # 获取日志保留天数配置
    retention_days = int(os.getenv("TASK_RETENTION_DAYS", 30))
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 使用当前时间作为日志文件名
    current_time = datetime.now().strftime("%Y%m%d")
    log_filename = f"{current_time}_{log_file}"

    # 创建TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(logs_dir, log_filename),
        when='midnight',
        interval=1,
        backupCount=retention_days,  # 使用环境变量中的保留天数
        encoding='utf-8'
    )

    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)

    return logger


# 创建通用信息日志记录器
logger = setup_logger('INFO', 'info.log')