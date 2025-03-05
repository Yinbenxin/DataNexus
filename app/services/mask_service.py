from typing import Dict, List, Tuple
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from sentence_transformers import SentenceTransformer
from paddlenlp import Taskflow
import datasets
from app.services.info_extract.info_extractor import InfoExtractor

from app.utils.logger import logger


default_schema = ['身份证号','姓名','出生日期','民族/种族','社交媒体账号','银行卡号','公司名称','证件号码','手机号','电子邮件地址','地址']


class MaskService:
    def __init__(self, embedding_model=None):
        self.information_extract = InfoExtractor()  
        logger.info("MaskService initialized, embedding model: {}".format(embedding_model))  
    def extract_keywords(self, schema: List[str], text: str) -> List[str]:
        keys_list = self.information_extract.extract_by_type(text, schema)
        return set(keys_list)

    def _generate_similar_text(self, text: str) -> str:
        """生成相似文本"""
        # 这里可以实现更复杂的相似文本生成逻辑
        return f"某{text[-1]}"

    def _type_replacement(self, text: str) -> str:
        """类型置换"""
        # 常见姓氏列表
        common_surnames = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许', '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章', '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳', '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常', '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹', '姚', '邵', '湛', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞', '熊', '纪', '舒', '屈', '项', '祝', '董', '梁', '杜', '阮', '蓝', '闵', '席', '季', '麻', '强', '贾', '路', '娄', '危', '江', '童', '颜', '郭', '梅', '盛', '林', '刁', '钟', '徐', '邱', '骆', '高', '夏', '蔡', '田', '樊', '胡', '凌', '霍', '虞', '万', '支', '柯', '昝', '管', '卢', '莫', '经', '房', '裘', '缪', '干', '解', '应', '宗', '丁', '宣', '贲', '邓', '郁', '单', '杭', '洪', '包', '诸', '左', '石', '崔', '吉', '钮', '龚', '程', '嵇', '邢', '滑', '裴', '陆', '荣', '翁', '荀', '羊', '於', '惠', '甄', '曲', '家', '封', '芮', '羿', '储', '靳', '汲', '邴', '糜', '松', '井', '段', '富', '巫', '乌', '焦', '巴', '弓', '牧', '隗', '山', '谷', '车', '侯', '宓', '蓬', '全', '郗', '班', '仰', '秋', '仲', '伊', '宫', '宁', '仇', '栾', '暴', '甘', '钭', '厉', '戎', '祖', '武', '符', '刘', '景', '詹', '束', '龙', '叶', '幸', '司', '韶', '郜', '黎', '蓟', '薄', '印', '宿', '白', '怀', '蒲', '邰', '从', '鄂', '索', '咸', '籍', '赖', '卓', '蔺', '屠', '蒙', '池', '乔', '阴', '郁', '胥', '能', '苍', '双', '闻', '莘', '党', '翟', '谭', '贡', '劳', '逄', '姬', '申', '扶', '堵', '冉', '宰', '郦', '雍', '郤', '璩', '桑', '桂', '濮', '牛', '寿', '通', '边', '扈', '燕', '冀', '郏', '浦', '尚', '农', '温', '别', '庄', '晏', '柴', '瞿', '阎', '充', '慕', '连', '茹', '习', '宦', '艾', '鱼', '容', '向', '古', '易', '慎', '戈', '廖', '庾', '终', '暨', '居', '衡', '步', '都', '耿', '满', '弘', '匡', '国', '文', '寇', '广', '禄', '阙', '东', '欧', '殳', '沃', '利', '蔚', '越', '夔', '隆', '师', '巩', '厍', '聂', '晁', '勾', '敖', '融', '冷', '訾', '辛', '阚', '那', '简', '饶', '空', '曾', '毋', '沙', '乜', '养', '鞠', '须', '丰', '巢', '关', '蒯', '相', '查', '后', '荆', '红', '游', '竺', '权', '逯', '盖', '益', '桓', '公', '万俟', '司马', '上官', '欧阳', '夏侯', '诸葛', '闻人', '东方', '赫连', '皇甫', '尉迟', '公羊', '澹台', '公冶', '宗政', '濮阳', '淳于', '单于', '太叔', '申屠', '公孙', '仲孙', '轩辕', '令狐', '钟离', '宇文', '长孙', '慕容', '鲜于', '闾丘', '司徒', '司空', '亓官', '司寇', '仉', '督', '子车', '颛孙', '端木', '巫马', '公西', '漆雕', '乐正', '壤驷', '公良', '拓跋', '夹谷', '宰父', '谷梁', '晋', '楚', '闫', '法', '汝', '鄢', '涂', '钦', '段干', '百里', '东郭', '南门', '呼延', '归', '海', '羊舌', '微生', '岳', '帅', '缑', '亢', '况', '后', '有', '琴', '梁丘', '左丘', '东门', '西门', '商', '牟', '佘', '佴', '伯', '赏', '南宫', '墨', '哈', '谯', '笪', '年', '爱', '阳', '佟', '第五', '言', '福']
        # 判断第一个字是否为姓氏
        if text[0] in common_surnames:
            return text[0] + "某"
        return f"某{text[-1]}"

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
                    # 统一处理文本替换和映射更新
                    if original_text in mapping or original_text in masked_text:
                        # 如果原文本在映射中，先替换映射值
                        if original_text in mapping:
                            masked_text = masked_text.replace(mapping[original_text], target_text)
                        # 如果原文本在文本中，直接替换
                        else:
                            masked_text = masked_text.replace(original_text, target_text)
                        # 更新映射关系
                        mapping[original_text] = target_text


        return masked_text, mapping

    async def process_mask(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None, force_convert: List[List[str]] = None) -> Tuple[str, Dict[str, str]]:
        """处理脱敏任务"""
        return await self.mask_text(text, mask_type, mask_model, mask_field, force_convert)
