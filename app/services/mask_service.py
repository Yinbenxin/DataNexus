from typing import Dict, List, Tuple
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
from paddlenlp import Taskflow
import datasets
from .info_extract.info_extractor import InfoExtractor

from app.utils.logger import logger
from .faker.faker import Faker


default_schema = ['身份证号','姓名','出生日期','民族/种族','社交媒体账号','银行卡号','公司名称','证件号码','手机号','电子邮件地址','地址']


class MaskService:
    def __init__(self, embedding_model=None):
        self.information_extract = InfoExtractor()  
        logger.info("MaskService initialized, embedding model: {}".format(embedding_model))  
        self.faker_generate = Faker()
    def extract_keywords(self, schema: List[str], text: str) -> (Dict[str, List[str]], Dict[str, List[str]]):
        keys_dict, keys_map = self.information_extract.extract_by_type(text, schema)
        # 使用列表推导式将所有值合并成一个列表
        return keys_dict, keys_map

    def _generate_similar_text(self, data_type: str, texts: List[str]) -> List[str]:
        """生成相似文本"""
        faker_data = self.faker_generate.generate(data_type, len(texts)) 
        return faker_data

    def _type_replacement(self, type: str, texts: List[str]) -> List[str]:
        """类型置换"""
        # 常见姓氏列表
        common_surnames = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许', '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章', '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳', '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常', '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹', '姚', '邵', '湛', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞', '熊', '纪', '舒', '屈', '项', '祝', '董', '梁', '杜', '阮', '蓝', '闵', '席', '季', '麻', '强', '贾', '路', '娄', '危', '江', '童', '颜', '郭', '梅', '盛', '林', '刁', '钟', '徐', '邱', '骆', '高', '夏', '蔡', '田', '樊', '胡', '凌', '霍', '虞', '万', '支', '柯', '昝', '管', '卢', '莫', '经', '房', '裘', '缪', '干', '解', '应', '宗', '丁', '宣', '贲', '邓', '郁', '单', '杭', '洪', '包', '诸', '左', '石', '崔', '吉', '钮', '龚', '程', '嵇', '邢', '滑', '裴', '陆', '荣', '翁', '荀', '羊', '於', '惠', '甄', '曲', '家', '封', '芮', '羿', '储', '靳', '汲', '邴', '糜', '松', '井', '段', '富', '巫', '乌', '焦', '巴', '弓', '牧', '隗', '山', '谷', '车', '侯', '宓', '蓬', '全', '郗', '班', '仰', '秋', '仲', '伊', '宫', '宁', '仇', '栾', '暴', '甘', '钭', '厉', '戎', '祖', '武', '符', '刘', '景', '詹', '束', '龙', '叶', '幸', '司', '韶', '郜', '黎', '蓟', '薄', '印', '宿', '白', '怀', '蒲', '邰', '从', '鄂', '索', '咸', '籍', '赖', '卓', '蔺', '屠', '蒙', '池', '乔', '阴', '郁', '胥', '能', '苍', '双', '闻', '莘', '党', '翟', '谭', '贡', '劳', '逄', '姬', '申', '扶', '堵', '冉', '宰', '郦', '雍', '郤', '璩', '桑', '桂', '濮', '牛', '寿', '通', '边', '扈', '燕', '冀', '郏', '浦', '尚', '农', '温', '别', '庄', '晏', '柴', '瞿', '阎', '充', '慕', '连', '茹', '习', '宦', '艾', '鱼', '容', '向', '古', '易', '慎', '戈', '廖', '庾', '终', '暨', '居', '衡', '步', '都', '耿', '满', '弘', '匡', '国', '文', '寇', '广', '禄', '阙', '东', '欧', '殳', '沃', '利', '蔚', '越', '夔', '隆', '师', '巩', '厍', '聂', '晁', '勾', '敖', '融', '冷', '訾', '辛', '阚', '那', '简', '饶', '空', '曾', '毋', '沙', '乜', '养', '鞠', '须', '丰', '巢', '关', '蒯', '相', '查', '后', '荆', '红', '游', '竺', '权', '逯', '盖', '益', '桓', '公', '万俟', '司马', '上官', '欧阳', '夏侯', '诸葛', '闻人', '东方', '赫连', '皇甫', '尉迟', '公羊', '澹台', '公冶', '宗政', '濮阳', '淳于', '单于', '太叔', '申屠', '公孙', '仲孙', '轩辕', '令狐', '钟离', '宇文', '长孙', '慕容', '鲜于', '闾丘', '司徒', '司空', '亓官', '司寇', '仉', '督', '子车', '颛孙', '端木', '巫马', '公西', '漆雕', '乐正', '壤驷', '公良', '拓跋', '夹谷', '宰父', '谷梁', '晋', '楚', '闫', '法', '汝', '鄢', '涂', '钦', '段干', '百里', '东郭', '南门', '呼延', '归', '海', '羊舌', '微生', '岳', '帅', '缑', '亢', '况', '后', '有', '琴', '梁丘', '左丘', '东门', '西门', '商', '牟', '佘', '佴', '伯', '赏', '南宫', '墨', '哈', '谯', '笪', '年', '爱', '阳', '佟', '第五', '言', '福']
        # 判断第一个字是否为姓氏
        return [text[0] + "某" if text[0] in common_surnames else f"某{text[-1]}" for text in texts]

    def _aes_encrypt(self, type: str, texts: List[str]) -> List[str]:
        """AES加密"""
        key = os.getenv("AES_KEY", "0123456789abcdef").encode('utf-8')  # 16字节密钥
        cipher = AES.new(key, AES.MODE_CBC)
        return [base64.b64encode(cipher.iv + cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))).decode('utf-8') for text in texts]

    def _md5_hash(self, type: str, texts: List[str]) -> List[str]:
        """MD5脱敏"""
        return [hashlib.md5(text.encode('utf-8')).hexdigest() for text in texts]

    def _sha256_hash(self, type: str, texts: List[str]) -> List[str]:
        """SHA256脱敏"""
        return [hashlib.sha256(text.encode('utf-8')).hexdigest() for text in texts]

    def _delete_text(self, type: str, texts: List[str]) -> List[str]:
        """删除文本"""
        return [""] * len(texts)

    def _mask_with_asterisk(self, type: str, texts: List[str]) -> List[str]:
        """使用星号掩码"""
        return ['*' * len(text) for text in texts]

    async def mask_text(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None, force_convert: List[List[str]] = None) -> (str, Dict[str, str], Dict[str, List[str]]):
        """对文本进行脱敏处理"""
        # 首先处理强制转换
        masked_text = text
        mapping = {}
        # 提取关键词
        keywords, keywords_map = self.extract_keywords(mask_field, masked_text)
        logger.info("keywords: {}".format(keywords))

        if len(keywords) == 0:
            return masked_text, mapping, {}

        mask_type_smart = mask_type.lower()
        # 根据不同的脱敏类型选择处理函数
        mask_func = {
            "similar": self._generate_similar_text,
            "type_replace": self._type_replacement,
            "delete": self._delete_text,
            "aes": self._aes_encrypt,
            "md5": self._md5_hash,
            "sha256": self._sha256_hash,
            "asterisk": self._mask_with_asterisk
        }.get(mask_type_smart)
        force_convert_key = []
        if not mask_func:
            raise ValueError(f"不支持的脱敏类型：{mask_type}")
        # 首先处理强制转换
        if force_convert:
            for convert_pair in force_convert:
                if len(convert_pair) == 2:
                    original_text, target_text = convert_pair
                    if original_text in masked_text:
                        masked_text = masked_text.replace(original_text, target_text)
                        mapping[original_text] = target_text
                        force_convert_key.append(original_text)
                else:
                    logger.warning(f"强制转换列表中的项 {convert_pair} 不符合格式，跳过")

        # 处理每种类型的文本
        for field_type, field_values in keywords.items():
            if field_values:  # 只处理非空列表
                masked_values = mask_func(field_type, field_values)
                # 更新映射关系和文本
                for original, masked in zip(field_values, masked_values):
                    # 检查是否在强制转换列表中
                    if original in force_convert_key:
                        continue
                    elif original in masked_text:
                        masked_text = masked_text.replace(original, masked)
                        mapping[original] = masked
                        keywords_map[original].append(masked)
        result_probability = [v.insert(1, k) or v for k, v in keywords_map.items()]
        logger.info("keywords: {}".format(result_probability))

        return masked_text, mapping, result_probability

    async def process_mask(self, text: str, mask_type: str = "similar", mask_model: str = "paddle", mask_field: List[str] = None, force_convert: List[List[str]] = None) -> (str, Dict[str, str], Dict[str, List[str]]):
        """处理脱敏任务"""
        return await self.mask_text(text, mask_type, mask_model, mask_field, force_convert)
