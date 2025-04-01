import unittest
import os
import requests
import json
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
call_back_url = "http://127.0.0.1:5001/rerank"

class CallbackHandler(BaseHTTPRequestHandler):
    received_data = {}
    lock = Lock()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        task_id = data.get('task_id')
        
        with CallbackHandler.lock:
            CallbackHandler.received_data[task_id] = data
        
        self.send_response(200)
        self.end_headers()

class BenchmarkRerankAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 从URL中解析主机和端口
        from urllib.parse import urlparse
        parsed_url = urlparse(call_back_url)
        cls.callback_host = parsed_url.hostname or '0.0.0.0'
        cls.callback_port = parsed_url.port

        cls.callback_server = HTTPServer((cls.callback_host, cls.callback_port), CallbackHandler)
        cls.server_thread = Thread(target=cls.callback_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    def setUp(self):
        """测试前的准备工作"""
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/rerank"
        self.headers = {"Content-Type": "application/json"}
        CallbackHandler.received_data = {}
        
        # 测试数据
        self.sample_query = "药品管理"
        with open("app/tests/data/law.txt", 'r', encoding='utf-8') as f:
            self.sample_texts = [line.strip() for line in f.readlines() if line.strip()]

    def create_rerank_task(self, query: str, texts: List[str], top_k: int = 3) -> Dict[str, Any]:
        """创建rerank任务并等待结果"""
        response = requests.post(
            self.base_url,
            json={
                "query": query,
                "texts": texts,
                "top_k": top_k,
                "handle": call_back_url
            },
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "创建任务失败")
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # 等待回调接收结果
        timeout = time.time() + 30  # 30秒超时
        while time.time() < timeout:
            with CallbackHandler.lock:
                if task_id in CallbackHandler.received_data:
                    result = CallbackHandler.received_data[task_id]
                    del CallbackHandler.received_data[task_id]
                    return result
            time.sleep(0.1)
        
        raise TimeoutError("等待回调超时")

    def test_texts_count_performance(self):
        """测试不同数量候选文本的处理时间"""
        test_counts = [10, 50, 100]
        results = []

        for count in test_counts:
            texts = self.sample_texts[:count] if count <= len(self.sample_texts) else self.sample_texts
            start_time = time.time()
            result = self.create_rerank_task(self.sample_query, texts)
            end_time = time.time()
            
            results.append({
                "texts_count": len(texts),
                "processing_time": end_time - start_time,
                "status": result["status"]
            })

        print("\n候选文本数量性能测试结果:")
        for result in results:
            print(f"文本数量: {result['texts_count']} 个")
            print(f"处理时间: {result['processing_time']:.2f} 秒")
            print(f"状态: {result['status']}\n")

    def test_query_length_performance(self):
        """测试不同长度查询的处理时间"""
        test_queries = [
            "药品",  # 短查询
            "药品管理和使用规范" * 2,  # 中等长度查询
            "医疗机构药品管理制度和使用规范" * 5  # 长查询
        ]

        results = []
        for query in test_queries:
            start_time = time.time()
            result = self.create_rerank_task(query, self.sample_texts[:20])
            end_time = time.time()
            
            results.append({
                "query_length": len(query),
                "processing_time": end_time - start_time,
                "status": result["status"]
            })

        print("\n查询长度性能测试结果:")
        for result in results:
            print(f"查询长度: {result['query_length']} 字符")
            print(f"处理时间: {result['processing_time']:.2f} 秒")
            print(f"状态: {result['status']}\n")

    def test_concurrent_requests(self):
        """测试并发请求的响应时间"""
        concurrent_counts = [5, 10]
        test_texts = self.sample_texts[:20]
        results = []

        def make_request():
            start_time = time.time()
            result = self.create_rerank_task(self.sample_query, test_texts)
            end_time = time.time()
            return end_time - start_time, result["status"]

        for count in concurrent_counts:
            print(f"\n测试 {count} 个并发请求...")
            with ThreadPoolExecutor(max_workers=count) as executor:
                futures = [executor.submit(make_request) for _ in range(count)]
                times = [future.result() for future in futures]

            processing_times = [t[0] for t in times]
            success_count = sum(1 for t in times if t[1] == "completed")
            error_count = count - success_count
            total_time = max(processing_times)
            qps = count / total_time if total_time > 0 else 0
            
            results.append({
                "concurrent_count": count,
                "avg_time": sum(processing_times) / len(processing_times),
                "min_time": min(processing_times),
                "max_time": max(processing_times),
                "success_rate": (success_count / count) * 100,
                "error_rate": (error_count / count) * 100,
                "qps": qps
            })

        print("\n并发请求性能测试结果:")
        for result in results:
            print(f"并发数: {result['concurrent_count']}")
            print(f"平均响应时间: {result['avg_time']:.2f} 秒")
            print(f"最小响应时间: {result['min_time']:.2f} 秒")
            print(f"最大响应时间: {result['max_time']:.2f} 秒")
            print(f"成功率: {result['success_rate']:.2f}%")
            print(f"错误率: {result['error_rate']:.2f}%")
            print(f"QPS: {result['qps']:.2f}\n")

    def test_system_stability(self):
        """测试系统在持续负载下的稳定性"""
        test_duration = 60  # 测试持续60秒
        request_interval = 1  # 每秒发送一个请求
        test_texts = self.sample_texts[:20]

        start_time = time.time()
        request_times = []
        success_count = 0
        fail_count = 0

        while time.time() - start_time < test_duration:
            try:
                request_start = time.time()
                result = self.create_rerank_task(self.sample_query, test_texts)
                request_time = time.time() - request_start
                request_times.append(request_time)
                if result["status"] == "completed":
                    success_count += 1
                else:
                    fail_count += 1

                # 等待到下一个间隔
                next_request = start_time + len(request_times) * request_interval
                sleep_time = max(0, next_request - time.time())
                time.sleep(sleep_time)

            except Exception as e:
                fail_count += 1
                print(f"请求失败: {str(e)}")

        total_requests = success_count + fail_count
        success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
        error_rate = (fail_count / total_requests) * 100 if total_requests > 0 else 0
        qps = len(request_times) / test_duration if test_duration > 0 else 0
        
        print("\n系统稳定性测试结果:")
        print(f"测试持续时间: {test_duration} 秒")
        print(f"总请求数: {total_requests}")
        print(f"成功请求数: {success_count}")
        print(f"失败请求数: {fail_count}")
        print(f"成功率: {success_rate:.2f}%")
        print(f"错误率: {error_rate:.2f}%")
        print(f"QPS: {qps:.2f}")
        print(f"平均响应时间: {sum(request_times)/len(request_times):.2f} 秒")
        print(f"最大响应时间: {max(request_times):.2f} 秒")
        print(f"最小响应时间: {min(request_times):.2f} 秒")

    def test_memory_usage(self):
        """测试内存使用情况"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 发送一系列请求并监控内存使用
        test_texts = self.sample_texts[:20]
        request_count = 10
        memory_samples = [initial_memory]

        for i in range(request_count):
            self.create_rerank_task(self.sample_query, test_texts)
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_samples.append(current_memory)

        print("\n内存使用测试结果:")
        print(f"初始内存使用: {initial_memory:.2f} MB")
        print(f"最终内存使用: {memory_samples[-1]:.2f} MB")
        print(f"内存增长: {memory_samples[-1] - initial_memory:.2f} MB")
        print(f"平均内存使用: {sum(memory_samples)/len(memory_samples):.2f} MB")
        print(f"最大内存使用: {max(memory_samples):.2f} MB")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'callback_server'):
            cls.callback_server.shutdown()
            cls.callback_server.server_close()
            cls.server_thread.join()

if __name__ == "__main__":
    unittest.main()