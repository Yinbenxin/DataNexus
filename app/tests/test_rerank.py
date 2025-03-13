import unittest
import os
import requests
import json
import time
from typing import Dict, Any, List, Tuple
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

class TestRerankAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 获取环境变量中的回调地址
        cls.handle_url = os.getenv('HANDLE_URL')
        if not cls.handle_url:
            raise ValueError('HANDLE_URL environment variable is not set')
        cls.handle_url = "http://192.168.101.122:61916"
        # 从URL中解析主机和端口
        from urllib.parse import urlparse
        parsed_url = urlparse(cls.handle_url)
        host = parsed_url.hostname or '0.0.0.0'
        port = parsed_url.port

        # 启动回调服务器
        cls.callback_server = HTTPServer((host, port), CallbackHandler)
        cls.server_thread = Thread(target=cls.callback_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL和回调URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/rerank"
        self.headers = {"Content-Type": "application/json"}
        self.callback_url = os.getenv('HANDLE_URL')
        
        # 测试数据
        self.sample_query = "药品管理"
        with open("app/tests/data/law.txt", 'r', encoding='utf-8') as f:
            self.sample_texts = [line.strip() for line in f.readlines() if line.strip()]

    def create_rerank_task(self, query: str, texts: List[str], top_k: int = 3) -> Dict[str, Any]:
        """创建rerank任务"""
        data = {
            "query": query,
            "texts": texts,
            "top_k": top_k,
            "handle": self.callback_url
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        return response.json()

    def test_rerank_normal(self):
        """测试正常的重排序请求"""
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

    def test_custom_top_k(self):
        """测试自定义top_k参数"""
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

    def test_empty_query(self):
        """测试空查询"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_rerank_task("", self.sample_texts)
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIsInstance(CallbackHandler.received_data["rankings"], list)

        # 验证每个排序结果的格式
        for rank_result in CallbackHandler.received_data["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    def test_empty_texts(self):
        """测试空候选文本列表"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_rerank_task(self.sample_query, [])
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertEqual(len(CallbackHandler.received_data["rankings"]), 0)

    def test_invalid_top_k(self):
        """测试无效的top_k参数（大于候选文本数量）"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_rerank_task(self.sample_query, self.sample_texts, top_k=10)
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertEqual(len(CallbackHandler.received_data["rankings"]), len(self.sample_texts))

        # 验证每个排序结果的格式
        for rank_result in CallbackHandler.received_data["rankings"]:
            self.assertIsInstance(rank_result, list)
            self.assertEqual(len(rank_result), 2)
            self.assertIsInstance(rank_result[0], str)
            self.assertIsInstance(rank_result[1], float)

    def test_invalid_query_params(self):
        """测试无效的查询参数"""
        # 测试非字符串类型的查询
        response = requests.post(self.base_url, json={"query": 123, "texts": self.sample_texts, "top_k": 3, "handle": self.callback_url}, headers=self.headers)
        self.assertEqual(response.status_code, 422, "非字符串类型的查询参数应该返回422状态码")

        # 测试过长的查询文本
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        long_query = "a" * 10000  # 创建一个非常长的查询文本
        result = self.create_rerank_task(long_query, self.sample_texts)
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIsInstance(CallbackHandler.received_data["rankings"], list)

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