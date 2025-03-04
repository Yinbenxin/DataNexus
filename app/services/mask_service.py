from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from sentence_transformers import SentenceTransformer
from paddlenlp import Taskflow
import datasets
from app.utils.logger import logger

load_dotenv()

default_schema = ['身份证号','姓名','出生日期','民族/种族','社交媒体账号','银行卡号','公司名称','证件号码','手机号','电子邮件地址','地址']


class MaskService:
    def __init__(self, embedding_model=None):
        # if embedding_model:
        #     self.model = embedding_model
        # else:
        #     self.model = SentenceTransformer('TencentBAC/Conan-embedding-v1')
        self.information_extract = Taskflow('information_extraction')  # 初始化时设置临时schema避免警告
        logger.info("MaskService initialized, embedding model: {}".format(embedding_model))  
    def extract_keywords(self, schema: List[str], text: str) -> List[str]:
        schema_set = set(schema+default_schema)
        self.information_extract.set_schema(schema_set)
        result = self.information_extract(text)
        keys_list = [entity['text'] for entity_type in result[0] for entity in result[0][entity_type]]
        return set(keys_list)

    def _generate_similar_text(self, text: str) -> str:
        """生成相似文本"""
        # 这里可以实现更复杂的相似文本生成逻辑
        return f"某{text[-1]}"

    def _type_replacement(self, text: str) -> str:
        """类型置换"""
        # 简单的类型置换逻辑
        type_map = {"张": "李", "王": "赵", "刘": "陈"}
        return type_map.get(text[0], "某") + text[1:]

    def _aes_encrypt(self, text: str) -> str:
        """AES加密"""
        key = os.getenv("AES_KEY", "0123456789abcdef").encode('utf-8')  # 16字节密钥
        cipher = AES.new(key, AES.MODE_CBC)
        padded_data = pad(text.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        return base64.b64encode(cipher.iv + encrypted_data).decode('utf-8')

    def _md5_hash(self, text: str) -> str:
        """MD5脱敏"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _sha256_hash(self, text: str) -> str:
        """SHA256脱敏"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _mask_with_asterisk(self, text: str) -> str:
        """使用星号掩码"""
        return '*' * len(text)

    async def mask_text(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None, force_convert: List[List[str]] = None) -> Tuple[str, Dict[str, str]]:
        """对文本进行脱敏处理"""
        # 首先处理强制转换
        masked_text = text
        mapping = {}
        # 提取关键词
        keywords = self.extract_keywords(mask_field, masked_text)
        if len(keywords) == 0:
            return masked_text, mapping

        mask_type_smart = mask_type.lower()
        for i, field in enumerate(keywords):
            if field in masked_text:
                mask_token = f"[MASK_{i}]"
                # 根据不同的脱敏类型处理
                if mask_type_smart == "similar":
                    masked_value = self._generate_similar_text(field)
                elif mask_type_smart == "type_replace":
                    masked_value = self._type_replacement(field)
                elif mask_type_smart == "delete":
                    masked_value = ""
                elif mask_type_smart == "aes":
                    masked_value = self._aes_encrypt(field)
                elif mask_type_smart == "md5":
                    masked_value = self._md5_hash(field)
                elif mask_type_smart == "sha256":
                    masked_value = self._sha256_hash(field)
                elif mask_type_smart == "asterisk":
                    masked_value = self._mask_with_asterisk(field)
                else:
                    raise ValueError(f"不支持的脱敏类型：{mask_type}")
                
                masked_text = masked_text.replace(field, masked_value)
                mapping[field] = masked_value

        if force_convert:
            for convert_pair in force_convert:
                if len(convert_pair) == 2:
                    original_text, target_text = convert_pair
                    if original_text in masked_text:
                        masked_text = masked_text.replace(original_text, target_text)
                        mapping[original_text] = target_text


        return masked_text, mapping

    async def process_mask(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None, force_convert: List[List[str]] = None) -> Tuple[str, Dict[str, str]]:
        """处理脱敏任务"""
        return await self.mask_text(text, mask_type, mask_model, mask_field, force_convert)
