import unittest
import os
import requests
import json
import time
from typing import Dict, Any, List, Tuple

class TestRerankAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/rerank"
        self.headers = {"Content-Type": "application/json"}
        
        # 测试数据
        self.sample_query = "药品管理"

        with open("app/tests/data/law.txt", 'r', encoding='utf-8') as f:
            self.sample_texts = [line.strip() for line in f.readlines() if line.strip()]

    def create_rerank_task(self, query: str, texts: List[str], top_k: int = 3) -> Dict[str, Any]:
        """创建rerank任务并等待结果"""
        data = {
            "query": query,
            "texts": texts,
            "top_k": top_k
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

    def test_rerank_normal(self):
        """测试正常的重排序请求"""
        result = self.create_rerank_task(self.sample_query, self.sample_texts)
        self.assertEqual(result["status"], "completed")
        self.assertIsInstance(result["rankings"], list)
        self.assertEqual(len(result["rankings"]), 3)  # 默认top_k=3
        print(result)
        # 验证每个排序结果的格式
        for rank_result in result["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)
            self.assertTrue(0 <= rank_result[1] <= 1)  # 分数应该在0到1之间

    def test_custom_top_k(self):
        """测试自定义top_k参数"""
        result = self.create_rerank_task(self.sample_query, self.sample_texts, top_k=2)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["rankings"]), 2)
        
        # 验证每个排序结果的格式
        for rank_result in result["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    def test_empty_query(self):
        """测试空查询"""
        result = self.create_rerank_task("", self.sample_texts)
        self.assertEqual(result["status"], "completed")
        self.assertIsInstance(result["rankings"], list)
        
        # 验证每个排序结果的格式
        for rank_result in result["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    def test_empty_texts(self):
        """测试空候选文本列表"""
        result = self.create_rerank_task(self.sample_query, [])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["rankings"]), 0)

    def test_invalid_top_k(self):
        """测试无效的top_k参数（大于候选文本数量）"""
        result = self.create_rerank_task(self.sample_query, self.sample_texts, top_k=10)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["rankings"]), len(self.sample_texts))
        
        # 验证每个排序结果的格式
        for rank_result in result["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    def test_invalid_query_params(self):
        """测试无效的查询参数"""
        # 测试非字符串类型的查询
        response = requests.post(self.base_url, json={"query": 123, "texts": self.sample_texts, "top_k": 3}, headers=self.headers)
        self.assertEqual(response.status_code, 422, "非字符串类型的查询参数应该返回422状态码")

        # 测试过长的查询文本
        long_query = "a" * 10000  # 创建一个非常长的查询文本
        result = self.create_rerank_task(long_query, self.sample_texts)
        self.assertEqual(result["status"], "completed")
        self.assertIsInstance(result["rankings"], list)
        
        # 验证每个排序结果的格式
        for rank_result in result["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

if __name__ == "__main__":
    unittest.main()