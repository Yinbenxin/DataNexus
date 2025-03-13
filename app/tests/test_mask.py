import unittest
import requests
import json
import time
import os
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
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

class TestMaskAPI(unittest.TestCase):
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
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/mask"
        self.headers = {"Content-Type": "application/json"}
        self.sample_text = "2024年2月17日，李明在北京参加了第十届世界人工智能峰会。该活动由国际人工智能协会主办，并在国家会议中心举行。"
        self.mask_fields = ["日期", "姓名", "职业", "地区", "外国人名"]

    def create_mask_task(self, mask_type: str) -> Dict[str, Any]:
        """创建脱敏任务"""
        # 重置回调数据
        CallbackHandler.received_data = None

        data = {
            "text": self.sample_text,
            "mask_type": mask_type,
            "mask_model": "paddle",
            "mask_field": self.mask_fields,
        }

        # 创建任务
        response = requests.post(self.base_url, json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200, "创建任务失败")
        return response.json()

    def wait_for_callback(self, timeout: int = 30) -> Dict[str, Any]:
        """等待回调结果"""
        end_time = time.time() + timeout
        while not CallbackHandler.received_data and time.time() < end_time:
            time.sleep(1)

        self.assertIsNotNone(CallbackHandler.received_data, "未收到回调数据")
        return CallbackHandler.received_data

    def test_similar_mask(self):
        """测试相似文本脱敏"""
        result = self.create_mask_task("similar")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])

        print("callback_data: ", callback_data)

    def test_type_replace_mask(self):
        """测试类型替换脱敏"""
        result = self.create_mask_task("type_replace")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_delete_mask(self):
        """测试删除脱敏"""
        result = self.create_mask_task("delete")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_aes_mask(self):
        """测试AES加密脱敏"""
        result = self.create_mask_task("aes")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_md5_mask(self):
        """测试MD5脱敏"""
        result = self.create_mask_task("md5")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_sha256_mask(self):
        """测试SHA256脱敏"""
        result = self.create_mask_task("sha256")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_asterisk_mask(self):
        """测试星号掩码脱敏"""
        result = self.create_mask_task("asterisk")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "completed")
        self.assertIsNotNone(callback_data["masked_text"])
        self.assertIsNotNone(callback_data["mapping"])
        print("callback_data: ", callback_data)

    def test_invalid_mask_type(self):
        """测试无效的脱敏类型"""
        result = self.create_mask_task("invalid_type")
        self.assertIsNotNone(result["task_id"])
        
        callback_data = self.wait_for_callback()
        self.assertEqual(callback_data["status"], "failed")
        print("callback_data: ", callback_data)

    @classmethod
    def tearDownClass(cls):
        # 关闭回调服务器
        cls.callback_server.shutdown()
        cls.callback_server.server_close()
        cls.server_thread.join()