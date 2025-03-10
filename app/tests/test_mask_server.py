import unittest
import json
import os
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
load_dotenv()

class CallbackHandler(BaseHTTPRequestHandler):
    received_data = []

    def do_POST(self):
        """处理POST请求，接收回调数据"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
            CallbackHandler.received_data.append(data)
            print(f"收到回调数据: {data}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON data")

class TestMaskServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """启动回调服务器"""
        # 从环境变量获取回调地址
        handle_url = os.getenv('HANDLE')
        if not handle_url:
            raise ValueError("环境变量HANDLE未设置")

        # 解析URL获取主机和端口
        parsed_url = urlparse(handle_url.strip('"'))
        host = parsed_url.hostname or '127.0.0.1'
        port = parsed_url.port

        if not port:
            raise ValueError("HANDLE环境变量中未指定端口")

        # 创建并启动服务器
        cls.server = HTTPServer((host, port), CallbackHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        print(f"回调服务器已启动，监听地址: {host}:{port}")

    def setUp(self):
        """每个测试用例开始前清空接收到的数据"""
        CallbackHandler.received_data = []

    def test_server_running(self):
        """测试服务器是否正常运行"""
        self.assertTrue(self.server_thread.is_alive())

    @classmethod
    def tearDownClass(cls):
        """关闭服务器"""
        print("正在关闭回调服务器...")
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()
        print("回调服务器已关闭")

    def handle_sigterm(signum, frame):
        """处理SIGTERM信号，确保服务器正常关闭"""
        print("收到SIGTERM信号，准备关闭服务器...")
        if hasattr(TestMaskServer, 'server'):
            TestMaskServer.server.shutdown()
            TestMaskServer.server.server_close()
        exit(0)

    def test_create_mask_task(self):
        """测试创建脱敏任务"""
        # 准备测试数据
        data = {
            "text": "2024年2月17日，李明在北京参加了第十届世界人工智能峰会。",
            "mask_type": "similar",
            "mask_model": "paddle",
            "mask_field": ["日期", "姓名", "地区"]
        }

        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API URL
        api_url = f"http://{api_host}:{api_port}/api/{api_version}/mask"
        headers = {"Content-Type": "application/json"}

        # 发送请求
        response = requests.post(api_url, json=data, headers=headers)
        
        # 验证响应
        self.assertEqual(response.status_code, 200, "创建任务应返回200状态码")
        result = response.json()
        
        # 验证返回的数据格式
        self.assertIn("task_id", result, "响应中应包含task_id字段")
        self.assertIsInstance(result["task_id"], str, "task_id应为字符串类型")
        self.assertTrue(len(result["task_id"]) > 0, "task_id不应为空")

if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGTERM, TestMaskServer.handle_sigterm)
    signal.signal(signal.SIGINT, TestMaskServer.handle_sigterm)

    try:
        unittest.main()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")