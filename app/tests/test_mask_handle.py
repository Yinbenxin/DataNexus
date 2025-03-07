import unittest
import requests
import json
import time
import os
from typing import Dict, Any
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

class TestMaskHandleAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 启动回调服务器
        cls.callback_server = HTTPServer(('192.168.100.138', 0), CallbackHandler)
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
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/mask"
        self.headers = {"Content-Type": "application/json"}
        self.sample_text = "2024年2月17日，李明在北京参加了第十届世界人工智能峰会。该活动由国际人工智能协会主办，并在国家会议中心举行。"
        self.mask_fields = ["日期", "姓名", "职业", "地区", "外国人名"]
        self.callback_url = f"http://192.168.100.138:{self.server_port}/callback"

    def create_mask_task(self, mask_type: str, handle: bool = True) -> Dict[str, Any]:
        """创建脱敏任务"""
        data = {
            "text": self.sample_text,
            "mask_type": mask_type,
            "mask_model": "paddle",
            "mask_field": self.mask_fields
        }
        if handle:
            data["handle"] = self.callback_url

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        return response.json()

    def test_similar_mask_handle(self):
        """测试相似文本脱敏的handle模式"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 创建任务
        result = self.create_mask_task("similar")
        self.assertIsNotNone(result["task_id"])

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIsNotNone(CallbackHandler.received_data["masked_text"])
        self.assertIsNotNone(CallbackHandler.received_data["mapping"])

    def test_invalid_callback_url(self):
        """测试无效的回调URL"""
        data = {
            "text": self.sample_text,
            "mask_type": "similar",
            "mask_model": "paddle",
            "mask_field": self.mask_fields,
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

    def test_force_convert_handle(self):
        """测试强制文本转换的handle模式"""
        # 重置回调数据
        CallbackHandler.received_data = None

        # 准备测试数据
        data = {
            "text": self.sample_text,
            "mask_type": "similar",
            "mask_model": "paddle",
            "mask_field": self.mask_fields,
            "force_convert": [["北京", "上海"], ["人工智能", "AI"]],
            "handle": self.callback_url
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")

        # 等待回调结果
        timeout = time.time() + 30  # 30秒超时
        while not CallbackHandler.received_data and time.time() < timeout:
            time.sleep(1)

        # 验证回调结果
        self.assertIsNotNone(CallbackHandler.received_data)
        self.assertEqual(CallbackHandler.received_data["status"], "completed")
        self.assertIn("上海", CallbackHandler.received_data["masked_text"])
        self.assertNotIn("北京", CallbackHandler.received_data["masked_text"])
        self.assertIn("AI", CallbackHandler.received_data["masked_text"])
        self.assertNotIn("人工智能", CallbackHandler.received_data["masked_text"])

    @classmethod
    def tearDownClass(cls):
        # 关闭回调服务器
        cls.callback_server.shutdown()
        cls.callback_server.server_close()
        cls.server_thread.join()

if __name__ == "__main__":
    unittest.main()