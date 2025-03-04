import unittest
import requests
import json
import time
import os
from typing import Dict, Any

class TestMaskAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/mask"
        self.headers = {"Content-Type": "application/json"}
        self.sample_text = "2024年2月17日，李明在北京参加了第十届世界人工智能峰会。该活动由国际人工智能协会主办，并在国家会议中心举行。"
        self.mask_fields = ["日期", "姓名", "职业", "地区", "外国人名", "时间"]

    def create_mask_task(self, mask_type: str) -> Dict[str, Any]:
        """创建脱敏任务并等待结果"""
        data = {
            "text": self.sample_text,
            "mask_type": mask_type,
            "mask_model": "paddle",
            "mask_field": self.mask_fields
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # 等待任务完成
        while True:
            response = requests.get(f"{self.base_url}/{task_id}")
            result = response.json()
            
            if result["status"] in ["completed", "failed"]:
                return result
            
            time.sleep(1)

    def test_similar_mask(self):
        """测试相似文本脱敏"""
        result = self.create_mask_task("similar")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_type_replace_mask(self):
        """测试类型替换脱敏"""
        result = self.create_mask_task("type_replace")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_delete_mask(self):
        """测试删除脱敏"""
        result = self.create_mask_task("delete")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_aes_mask(self):
        """测试AES加密脱敏"""
        result = self.create_mask_task("aes")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_md5_mask(self):
        """测试MD5脱敏"""
        result = self.create_mask_task("md5")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_sha256_mask(self):
        """测试SHA256脱敏"""
        result = self.create_mask_task("sha256")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_asterisk_mask(self):
        """测试星号掩码脱敏"""
        result = self.create_mask_task("asterisk")
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])

    def test_invalid_mask_type(self):
        """测试无效的脱敏类型"""
        data = {
            "text": self.sample_text,
            "mask_type": "invalid_type",
            "mask_model": "paddle",
            "mask_field": self.mask_fields
        }
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # 等待任务完成
        result = None
        while True:
            response = requests.get(f"{self.base_url}/{task_id}")
            result = response.json()
            if result["status"] in ["completed", "failed"]:
                break
            time.sleep(1)
        
        self.assertEqual(result["status"], "failed")

    def test_force_convert(self):
        """测试强制文本转换"""
        # 准备测试数据
        data = {
            "text": self.sample_text,
            "mask_type": "similar",
            "mask_model": "paddle",
            "mask_field": self.mask_fields,
            "force_convert": [["北京", "上海"], ["人工智能", "AI"]]
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # 等待任务完成
        result = None
        while True:
            response = requests.get(f"{self.base_url}/{task_id}")
            result = response.json()
            if result["status"] in ["completed", "failed"]:
                break
            time.sleep(1)

        # 验证结果
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["masked_text"])
        self.assertIsNotNone(result["mapping"])
        
        # 验证强制转换是否生效
        self.assertIn("上海", result["masked_text"])
        self.assertNotIn("北京", result["masked_text"])
        self.assertIn("AI", result["masked_text"])
        self.assertNotIn("人工智能", result["masked_text"])
        
        # 验证映射关系
        self.assertEqual(result["mapping"]["北京"], "上海")
        self.assertEqual(result["mapping"]["人工智能"], "AI")

if __name__ == "__main__":
    unittest.main()