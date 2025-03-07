import unittest
import requests
import json
import time
import os
from typing import Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class CallbackHandler(BaseHTTPRequestHandler):
    received_data = None

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        CallbackHandler.received_data = json.loads(post_data.decode('utf-8'))
        self.send_response(200)
        self.end_headers()

class TestRerankHandleAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 启动回调服务器
        cls.callback_server = HTTPServer(('0.0.0.0', 0), CallbackHandler)
        cls.server_port = cls.callback_server.server_address[1]
        cls.server_thread = Thread(target=cls.callback_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/rerank"
        self.headers = {"Content-Type": "application/json"}
        self.callback_url = f"http://192.168.100.138:{self.server_port}/callback"
        
        # 测试数据
        self.sample_query = "药品管理"
        with open("app/tests/data/law.txt", 'r', encoding='utf-8') as f:
            self.sample_texts = [line.strip() for line in f.readlines() if line.strip()]

    def create_rerank_task(self, query: str, texts: List[str], top_k: int = 3, handle: bool = True) -> Dict[str, Any]:
        """创建rerank任务"""
        data = {
            "query": query,
            "texts": texts,
            "top_k": top_k
        }
        if handle:
            data["handle"] = self.callback_url

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        return response.json()

    def test_rerank_handle_normal(self):
        """测试正常的重排序handle请求"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_rerank_task(self.sample_query, self.sample_texts)
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIsInstance(CallbackHandler.received_data["rankings"], list)
        self.assertEqual(len(CallbackHandler.received_data["rankings"]), 3)  # 默认top_k=3

        # 验证每个排序结果的格式
        for rank_result in CallbackHandler.received_data["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)
            self.assertTrue(0 <= rank_result[1] <= 1)  # 分数应该在0到1之间

    def test_invalid_callback_url(self):
        """测试无效的回调URL"""
        data = {
            "query": self.sample_query,
            "texts": self.sample_texts,
            "top_k": 3,
            "handle": "http://invalid-url:12345/callback"
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        task_data = response.json()
        self.assertIsNotNone(task_data["task_id"])

        # 验证任务状态
        time.sleep(5)  # 等待一段时间让任务处理
        response = requests.get(f"{self.base_url}/{task_data['task_id']}")
        result = response.json()
        self.assertEqual(result["status"], "completed")

    def test_custom_top_k_handle(self):
        """测试自定义top_k参数的handle模式"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_rerank_task(self.sample_query, self.sample_texts, top_k=2)
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertEqual(len(CallbackHandler.received_data["rankings"]), 2)

        # 验证每个排序结果的格式
        for rank_result in CallbackHandler.received_data["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    @classmethod
    def tearDownClass(cls):
        # 关闭回调服务器
        cls.callback_server.shutdown()
        cls.callback_server.server_close()
        cls.server_thread.join()

if __name__ == "__main__":
    unittest.main()