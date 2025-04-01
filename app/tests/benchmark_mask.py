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
call_back_url = "http://127.0.0.1:5001/mask"

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

class BenchmarkMaskAPI(unittest.TestCase):
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
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/mask"
        self.headers = {"Content-Type": "application/json"}
        CallbackHandler.received_data = {}
        
        # 测试数据
        self.sample_text = "12月30日早晨,DeepMind在Y(原脸书)上发文宣布,约瑟夫·安德森(Joseph Anderson)将正式回归DeepMind,重新担任CEO,同时DeepMind的董事会将迎来重组。具体来看,Oracle联席CEO詹姆斯沃克、前英国财政部部长、颇具影响力的英国经济学家约翰·史密斯和lnnoveCEO罗伯特·约翰逊(RobertJohnson)将组成新的初始董事会成员。"
        self.mask_fields = ["日期", "姓名", "职业", "地区", "外国人名"]
        self.force_convert = [["DeepMind", "深度思考"],["董事会成员","领导班子"]]

    def create_mask_task(self, text: str, mask_type: str = "similar") -> Dict[str, Any]:
        """创建脱敏任务并等待结果"""
        response = requests.post(
            self.base_url,
            json={
                "text": text,
                "mask_type": mask_type,
                "mask_model": "paddle",
                "mask_field": self.mask_fields,
                "force_convert": self.force_convert,
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

    def test_text_length_performance(self):
        """测试不同长度文本的处理时间"""
        test_texts = [
            self.sample_text[:50],  # 短文本
            self.sample_text,  # 中等长度文本
            self.sample_text * 3,  # 长文本
        ]

        results = []
        for text in test_texts:
            start_time = time.time()
            result = self.create_mask_task(text)
            end_time = time.time()
            
            results.append({
                "text_length": len(text),
                "processing_time": end_time - start_time,
                "status": result["status"]
            })

        print("\n文本长度性能测试结果:")
        for result in results:
            print(f"文本长度: {result['text_length']} 字符")
            print(f"处理时间: {result['processing_time']:.2f} 秒")
            print(f"状态: {result['status']}\n")

    def test_mask_type_performance(self):
        """测试不同脱敏类型的处理时间"""
        mask_types = ["similar", "type_replace", "delete", "aes", "md5", "sha256", "asterisk"]
        results = []

        for mask_type in mask_types:
            start_time = time.time()
            result = self.create_mask_task(self.sample_text, mask_type)
            end_time = time.time()
            
            results.append({
                "mask_type": mask_type,
                "processing_time": end_time - start_time,
                "status": result["status"]
            })

        print("\n脱敏类型性能测试结果:")
        for result in results:
            print(f"脱敏类型: {result['mask_type']}")
            print(f"处理时间: {result['processing_time']:.2f} 秒")
            print(f"状态: {result['status']}\n")

    def test_concurrent_requests(self):
        """测试并发请求的响应时间"""
        concurrent_counts = [5, 10]
        results = []

        def make_request():
            start_time = time.time()
            result = self.create_mask_task(self.sample_text)
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

        start_time = time.time()
        request_times = []
        success_count = 0
        fail_count = 0

        while time.time() - start_time < test_duration:
            try:
                request_start = time.time()
                result = self.create_mask_task(self.sample_text)
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



    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'callback_server'):
            cls.callback_server.shutdown()
            cls.callback_server.server_close()
            cls.server_thread.join()

if __name__ == "__main__":
    unittest.main()