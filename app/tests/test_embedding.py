import unittest
import os
import requests
import json
import time
import asyncio
from aiohttp import web
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

class TestEmbeddingAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        self.callback_host = "127.0.0.1"
        self.callback_port = 61916
        self.handle_url = "http://127.0.0.1:61916/callback"
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/embedding"
        self.headers = {"Content-Type": "application/json"}
        
        # 设置回调相关的属性
        self.callback_received = False
        self.callback_data = None
        
    async def callback_handler(self, request):
        """处理回调请求"""
        self.callback_received = True
        self.callback_data = await request.json()
        return web.Response(text="OK")
    
    async def start_callback_server(self):
        """启动回调服务器"""
        app = web.Application()
        app.router.add_post("/callback", self.callback_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.callback_host, int(self.callback_port))
        await site.start()
        return runner
    
    async def test_embedding_with_callback_async(self):
        """测试带回调的embedding生成"""
        # 启动回调服务器
        runner = await self.start_callback_server()
        
        try:
            # 创建带handle参数的embedding任务
            response = requests.post(
                self.base_url,
                json={
                    "text": "测试文本",
                },
                headers=self.headers
            )
            
            # 验证任务创建成功
            self.assertEqual(response.status_code, 200)
            task_data = response.json()
            self.assertTrue("task_id" in task_data)
            self.assertTrue(task_data["success"])
            
            # 等待回调接收结果
            start_time = time.time()
            while not self.callback_received and time.time() - start_time < 30:
                await asyncio.sleep(1)
            
            # 验证回调接收到结果
            self.assertTrue(self.callback_received)
            self.assertIsNotNone(self.callback_data)
            
            # 验证回调数据的正确性
            self.assertEqual(self.callback_data["task_id"], task_data["task_id"])
            self.assertEqual(self.callback_data["status"], "completed")
            self.assertIsInstance(self.callback_data["embedding"], list)
            
        finally:
            # 停止回调服务器
            await runner.cleanup()
    
    def test_embedding_with_callback(self):
        """同步方法调用异步测试"""
        asyncio.run(self.test_embedding_with_callback_async())
    
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

if __name__ == "__main__":
    unittest.main()