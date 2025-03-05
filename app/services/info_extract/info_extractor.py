import re
import os

from typing import  List
from paddlenlp import Taskflow
from .config import FIXED_TYPES, CONVERT_MAP
from app.utils.logger import logger

class InfoExtractor:
    # 支持的信息类型及其描述

    def __init__(self):
        self.FIXED_TYPES = FIXED_TYPES
        self.CONVERT_MAP = CONVERT_MAP
        model_name_or_path=os.getenv("INFO_EXTRACT_MODEL_PATH")
        if model_name_or_path=="":
            model_name_or_path = 'uie-tiny'
        logger.info(f"信息抽取模型加载中, 模型路径: {model_name_or_path}")
        self.information_extract = Taskflow('information_extraction',  schema=["临时schema"], task_path=model_name_or_path)  # 初始化时设置临时schema避免警告
        logger.info(f"信息抽取模型加载完成, 模型路径: {model_name_or_path}")
    def extract_by_pattern(self, text, pattern):
        """统一的正则表达式提取方法"""
        return re.findall(pattern, text)
    
    def extract_all(self, text):
        """提取所有类型的信息"""
        return {info_type: self.extract_by_pattern(text, pattern)
                for info_type, pattern in self.FIXED_TYPES.items()}
    
    def extract_by_type(self, text, info_types)-> List[str]:
        """根据指定的类型提取信息

        Args:
            text: 要提取信息的文本
            info_types: 信息类型列表或单个类型，可选值包括InfoExtractor.FIXED_TYPES中定义的类型

        Returns:
            List[str]: 提取到的信息列表

        """
        # 如果传入的是单个类型字符串，转换为列表
        if isinstance(info_types, str):
            info_types = [info_types]

        # 如果属于FIXED_TYPES则使用extract_by_fixed_type，否则使用extract_by_other_type
        info_extract_types = set(info_types)
        info_types_by_fixed = []
        info_types_by_other = []
        for i in info_extract_types:
            if i in self.FIXED_TYPES:
                info_types_by_fixed.append(i)
            else:
                if i in self.CONVERT_MAP:
                    info_types_by_other.append(self.CONVERT_MAP[i])
                else:
                    info_types_by_other.append(i)
        info_extract_by_fixed=self.extract_by_fixed_type(text, info_types_by_fixed)
        info_extract_by_other=self.extract_by_other_type(text, info_types_by_other)
        return info_extract_by_fixed+info_extract_by_other

    def extract_by_fixed_type(self, text, info_types)-> List[str]:
        """根据指定的类型提取信息
        
        Args:
            text: 要提取信息的文本
            info_types: 信息类型列表或单个类型，可选值包括InfoExtractor.FIXED_TYPES中定义的类型
        
        Returns:
            List[str]: 提取到的信息列表

        """
        # 如果传入的是单个类型字符串，转换为列表
        if isinstance(info_types, str):
            info_types = [info_types]
            
        # 验证所有类型是否合法
        invalid_types = [t for t in info_types if t not in self.FIXED_TYPES]
        if invalid_types:
            raise ValueError(f'不支持的信息类型：{invalid_types}')
        
        # 提取指定类型的信息并合并结果
        results = []
        for info_type in info_types:
            results.extend(self.extract_by_pattern(text, self.FIXED_TYPES[info_type]))
        return results
    
    def extract_by_other_type(self, text, info_types)-> List[str]:
        schema_set = set(info_types)
        self.information_extract.set_schema(schema_set)
        result = self.information_extract(text)
        keys_list = [entity['text'] for entity_type in result[0] for entity in result[0][entity_type]]
        return keys_list
