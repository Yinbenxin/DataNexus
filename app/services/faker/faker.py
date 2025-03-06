import numpy as np
import json
import os
from faker import Faker as FakerGenerator
from typing import List, Dict, Any, Optional
from .config import FAKER_TYPES_MAP, OTHER_TYPE_MAP
from sentence_transformers import SentenceTransformer
from app.utils.logger import logger

class Faker:
    def __init__(self):
        """初始化Faker类，创建中文数据生成器"""
        self.zh_faker = FakerGenerator('zh_CN')
        
        # 加载JSON数据文件
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.current_dir, 'faker_data')
        self._init_model_embeddings()

    def _init_model_embeddings(self):
        model_name_or_path=os.getenv("EMBEDDING_SMELL_ZH")
        logger.info("加载模型：EMBEDDING_SMELL_ZH: {}".format(model_name_or_path))
        if model_name_or_path:
            self.model = SentenceTransformer(model_name_or_path)
        else:
            self.model = SentenceTransformer('llm-model/bge-small-zh')
        logger.info("加载模型完成")
        all_type = list(FAKER_TYPES_MAP.keys())+list(OTHER_TYPE_MAP.keys())
        self.all_type_embeddings = self.model.encode(all_type, convert_to_tensor=True, normalize_embeddings=True)
    def similarity_type(self, data_type: str) -> List[tuple[float, str]]:
        """计算输入类型与预定义类型之间的相似度

        Args:
            data_type: 输入的数据类型

        Returns:
            按相似度降序排序的(相似度, 类型)元组列表
        """
        import torch.nn.functional as F
        data_type_embedding = self.model.encode(data_type, convert_to_tensor=True, normalize_embeddings=True)
        # 获取所有预定义类型
        all_types = list(FAKER_TYPES_MAP.keys()) + list(OTHER_TYPE_MAP.keys())
        
        # 计算相似度
        similarities = []
        for i, type_name in enumerate(all_types):
            similarity = F.cosine_similarity(data_type_embedding.unsqueeze(0), self.all_type_embeddings[i].unsqueeze(0))
            similarities.append((similarity.item(), type_name))

        # 按相似度降序排序
        similarities.sort(reverse=True)
        return similarities

    def _generate_faker_type(self, data_type: str, count: int) -> List[str]:
        """生成faker库支持的类型数据"""


        fake_data = []
        generated_data = set()
        method = getattr(self.zh_faker, FAKER_TYPES_MAP[data_type])
        while len(fake_data) < count:
            value = str(method())
            if value not in generated_data:
                fake_data.append(value)
                generated_data.add(value)
        return fake_data

    def _generate_other_type(self, data_type: str, count: int) -> List[str]:
        """生成其他类型数据（从JSON文件读取）"""
        file_path = os.path.join(self.data_dir, OTHER_TYPE_MAP[data_type])
        with open(file_path, 'r', encoding='utf-8') as file:
            available_data = json.load(file)
            # 确保要生成的数量不超过可用数据的数量
            if count > len(available_data):
                count = len(available_data)
            # 使用replace=False确保不重复选择
            selected_data = np.random.choice(available_data, size=count, replace=False)
            return list(selected_data)

    def generate(self, data_type: str, count: int = 1) -> List[str]:
        """生成指定类型和数量的假数据"""
        if count < 1:
            raise ValueError("数据数量必须大于0")
        similarity, similarities_type = self.similarity_type(data_type)[0]
        logger.info("相似度最高的类型: {}-->{}, 相似度:{}".format(data_type, similarities_type, similarity))
        if similarities_type in FAKER_TYPES_MAP:
            return self._generate_faker_type(similarities_type, count)
        elif similarities_type in OTHER_TYPE_MAP:
            return self._generate_other_type(similarities_type, count)
        else:
            return ['[UNKNOWN_TYPE]' for _ in range(count)]



