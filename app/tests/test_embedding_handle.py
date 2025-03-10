import unittest
import requests
import time
import asyncio
import os
from aiohttp import web
from app.models.redis_models import embedding_task_model
from app.utils.queue_manager import task_queue

class TestEmbeddingHandle(unittest.TestCase):
    def setUp(self):
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/embedding"
        self.headers = {"Content-Type": "application/json"}
        
        # 设置模拟回调服务器
        self.callback_received = False
        self.callback_data = None
        
    # def tearDown(self):
    #     # 清理测试数据
    #     asyncio.run(self.cleanup_test_data())
        
    # async def cleanup_test_data(self):
    #     # 清理Redis中的测试数据
    #     tasks = await task_queue.get_queue_status()
    #     for task_id in tasks.get("processing", []):
    #         await embedding_task_model.delete(task_id)
    
    async def callback_handler(self, request):
        # 模拟回调接口处理
        self.callback_received = True
        self.callback_data = await request.json()
        return web.Response(text="OK")
    
    async def start_callback_server(self):
        # 启动模拟回调服务器
        app = web.Application()
        app.router.add_post("/callback", self.callback_handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8888)
        await site.start()
        return runner
    
    async def test_embedding_with_handle_async(self):
        # 启动回调服务器
        runner = await self.start_callback_server()
        
        try:
            # 创建带handle参数的embedding任务
            response = requests.post(
                self.base_url,
                json={
                    "text": "测试文本",
                    "handle": "http://localhost:8888/callback"
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
            
            # 等待一段时间确保回调处理完成
            await asyncio.sleep(2)
            
        finally:
            # 停止回调服务器
            await runner.cleanup()
    
    def test_embedding_with_handle(self):
        # 使用asyncio运行异步测试
        asyncio.run(self.test_embedding_with_handle_async())

if __name__ == "__main__":
    unittest.main()