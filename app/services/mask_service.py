from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

load_dotenv()

class MaskService:
    def __init__(self):
        pass

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

    async def mask_text(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None) -> Tuple[str, Dict[str, str]]:
        """对文本进行脱敏处理"""
        if not mask_field:
            return text, {}
            
        masked_text = text
        mapping = {}
        for i, field in enumerate(mask_field):
            if field in text:
                mask_token = f"[MASK_{i}]"
                # 根据不同的脱敏类型处理
                if mask_type == "similar":
                    masked_value = self._generate_similar_text(field)
                elif mask_type == "type_replace":
                    masked_value = self._type_replacement(field)
                elif mask_type == "delete":
                    masked_value = ""
                elif mask_type == "aes":
                    masked_value = self._aes_encrypt(field)
                elif mask_type == "md5":
                    masked_value = self._md5_hash(field)
                elif mask_type == "sha256":
                    masked_value = self._sha256_hash(field)
                elif mask_type == "asterisk":
                    masked_value = self._mask_with_asterisk(field)
                else:
                    raise ValueError(f"不支持的脱敏类型：{mask_type}")
                
                masked_text = masked_text.replace(field, mask_token)
                mapping[mask_token] = masked_value
        return masked_text, mapping

    async def process_mask(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None) -> Tuple[str, Dict[str, str]]:
        """处理脱敏任务"""
        return await self.mask_text(text, mask_type, mask_model, mask_field)
