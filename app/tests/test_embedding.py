import unittest
import os
import requests
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import asyncio
from aiohttp import web
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

class CallbackHandler(BaseHTTPRequestHandler):
    received_data = None

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        CallbackHandler.received_data = json.loads(post_data.decode('utf-8'))
        self.send_response(200)
        self.end_headers()

class TestEmbeddingAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 初始化回调服务器
        cls.callback_host = "127.0.0.1"
        # cls.callback_host = "192.168.101.122"
        cls.callback_port = 61916
        cls.handle_url = f"http://{cls.callback_host}:{cls.callback_port}"
        cls.callback_server = HTTPServer((cls.callback_host, cls.callback_port), CallbackHandler)
        cls.server_thread = Thread(target=cls.callback_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")#本地
        # api_host = "192.168.101.122"

        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/embedding"
        self.headers = {"Content-Type": "application/json"}
        
        # 重置回调数据
        CallbackHandler.received_data = None

    def test_embedding_with_callback(self):
        """测试带回调的embedding生成"""
        # 创建带handle参数的embedding任务
        response = requests.post(
            self.base_url,
            json={
                "text": "测试文本",
                "handle": self.handle_url
            },
            headers=self.headers
        )
        print(response.json())
        # 验证任务创建成功
        self.assertEqual(response.status_code, 200)
        task_data = response.json()
        self.assertTrue("task_id" in task_data)
        self.assertTrue(task_data["success"])
        
        # 等待回调接收结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)
        
        # 验证回调接收到结果
        self.assertIsNotNone(CallbackHandler.received_data, "未收到回调数据")
        
        # 验证回调数据的正确性
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIsInstance(CallbackHandler.received_data["embedding"], list)
        print(CallbackHandler.received_data)

    def test_embedding_generation(self):
        """测试生成embedding"""
        sample_text = "2edca33b-dad9-49c3-a441-e5672d6b1429"
        result = self.create_embedding_task(sample_text)
        self.assertIn(result["status"], ["completed", "failed"])
        if result["status"] == "completed":
            self.assertIsNotNone(result["embedding"])
            self.assertEqual(result["text"], sample_text)
            print(len(result["embedding"]))
    
    def test_invalid_text(self):
        """测试无效的文本输入"""
        sample_text = ""
        result = self.create_embedding_task(sample_text)
        self.assertIn(result["status"], ["completed", "failed"])
        if result["status"] == "completed":
            self.assertIsNotNone(result["embedding"])
            print(len(result["embedding"]))
            self.assertEqual(result["text"], sample_text)

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

    @classmethod
    def tearDownClass(cls):
        # 关闭回调服务器
        if hasattr(cls, 'callback_server'):
            cls.callback_server.shutdown()
            cls.callback_server.server_close()
            cls.server_thread.join()

if __name__ == "__main__":
    unittest.main()