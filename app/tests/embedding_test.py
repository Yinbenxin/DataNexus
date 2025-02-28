import unittest
import os
import requests
import json
import time
from typing import Dict, Any

class TestEmbeddingAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/embedding"
        self.headers = {"Content-Type": "application/json"}

    def create_embedding_task(self, text) -> Dict[str, Any]:
        """创建embedding任务并等待结果"""
        # 创建任务
        response = requests.post(self.base_url, json={"text": text}, headers=self.headers)
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

    def test_embedding_generation(self):
        """测试生成embedding"""
        sample_text = "2edca33b-dad9-49c3-a441-e5672d6b1429"
        result = self.create_embedding_task(sample_text)
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["embedding"])
        self.assertEqual(result["text"], sample_text)
        print(len(result["embedding"]))

    def test_invalid_text(self):
        """测试无效的文本输入"""
        sample_text = ""
        result = self.create_embedding_task(sample_text)
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["embedding"])
        print(len(result["embedding"]))
        self.assertEqual(result["text"], sample_text)

if __name__ == "__main__":
    unittest.main()