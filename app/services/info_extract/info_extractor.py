import re
import os

from typing import  List, Dict
from paddlenlp import Taskflow
from .config import FIXED_TYPES, CONVERT_MAP
from app.utils.logger import logger

class InfoExtractor:
    # 支持的信息类型及其描述

    def __init__(self):
        self.FIXED_TYPES = FIXED_TYPES
        self.CONVERT_MAP = CONVERT_MAP
        logger.info(f"信息抽取模型加载, 模型路径: uie-medium")
        self.information_extract = Taskflow('information_extraction', schema=["临时schema"], model='uie-medium', padding='max_length')
        logger.info(f"信息抽取模型加载完成, 模型路径: uie-medium")
    def extract_by_pattern(self, text, pattern):
        """统一的正则表达式提取方法"""
        return re.findall(pattern, text)
    
    def extract_all(self, text):
        """提取所有类型的信息"""
        return {info_type: self.extract_by_pattern(text, pattern)
                for info_type, pattern in self.FIXED_TYPES.items()}
    
    def extract_by_type(self, text, info_types)-> Dict[str, List[str]]:
        """根据指定的类型提取信息

        Args:
            text: 要提取信息的文本
            info_types: 信息类型列表或单个类型，可选值包括InfoExtractor.FIXED_TYPES中定义的类型

        Returns:
            Dict[str, List[str]]: 提取到的信息字典，键为信息类型，值为对应的提取结果列表

        """
        # 如果传入的是单个类型字符串，转换为列表
        if isinstance(info_types, str):
            info_types = [info_types]

        # 如果属于FIXED_TYPES则使用extract_by_fixed_type，否则使用extract_by_other_type
        info_extract_types = set(info_types)
        info_types_by_fixed = []
        info_types_by_other = []
        result_dict = {}

        for i in info_extract_types:
            if i in self.FIXED_TYPES:
                info_types_by_fixed.append(i)
            else:
                if i in self.CONVERT_MAP:
                    info_types_by_other.append(self.CONVERT_MAP[i])
                    result_dict[i] = []
                else:
                    info_types_by_other.append(i)
                    result_dict[i] = []

        # 处理固定类型的提取结果
        if info_types_by_fixed:
            fixed_results = self.extract_by_fixed_type(text, info_types_by_fixed)
            for info_type, values in fixed_results.items():
                result_dict[info_type] = values

        # 处理其他类型的提取结果
        if info_types_by_other:
            other_results = self.extract_by_other_type(text, info_types_by_other)
            for info_type, result in zip(info_types_by_other, other_results):
                original_type = next((k for k, v in self.CONVERT_MAP.items() if v == info_type), info_type)
                result_dict[original_type] = result

        return result_dict

    def extract_by_fixed_type(self, text, info_types)-> Dict[str, List[str]]:
        """根据指定的类型提取信息
        
        Args:
            text: 要提取信息的文本
            info_types: 信息类型列表或单个类型，可选值包括InfoExtractor.FIXED_TYPES中定义的类型
        
        Returns:
            Dict[str, List[str]]: 提取到的信息字典，键为信息类型，值为对应的提取结果列表

        """
        # 如果传入的是单个类型字符串，转换为列表
        if isinstance(info_types, str):
            info_types = [info_types]
            
        # 验证所有类型是否合法
        invalid_types = [t for t in info_types if t not in self.FIXED_TYPES]
        if invalid_types:
            raise ValueError(f'不支持的信息类型：{invalid_types}')
        
        # 提取指定类型的信息并组织为字典
        results = {}
        for info_type in info_types:
            results[info_type] = self.extract_by_pattern(text, self.FIXED_TYPES[info_type])
        return results
    
    def extract_by_other_type(self, text, info_types)-> List[List[str]]:
        schema_set = set(info_types)
        self.information_extract.set_schema(schema_set)
        result = self.information_extract(text)
        results = []
        for info_type in info_types:
            type_results = []
            if info_type in result[0]:
                for entity in result[0][info_type]:
                    type_results.append(entity['text'])
            results.append(type_results)
        return results


