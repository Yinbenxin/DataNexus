import os
import unittest
import requests

class TestOCRAPI(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 从环境变量中读取API配置
        api_host = os.getenv("API_HOST", "127.0.0.1")
        api_port = os.getenv("API_PORT", "8000")
        api_version = os.getenv("API_VERSION", "v1")
        
        # 构建API基础URL
        self.base_url = f"http://{api_host}:{api_port}/api/{api_version}/ocr"
        self.headers = {"Content-Type": "application/octet-stream"}
        self.test_image_path = "app/tests/data/ocr发展史.png"

    def test_extract_image_text(self):
        """测试图片文本提取 - 成功场景"""
        # 读取测试图片数据
        with open(self.test_image_path, "rb") as f:
            image_data = f.read()

        # 发送请求
        response = requests.post(
            f"{self.base_url}/image",
            data=image_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "请求失败")

        # 获取结果
        result = response.json()
        self.assertIn("result", result, "返回结果中缺少'result'字段")
        self.assertIsInstance(result["result"], str, "OCR结果应该是字符串类型")
        self.assertGreater(len(result["result"]), 0, "OCR结果不应为空")
        
        # 打印提取结果
        print("\n=== OCR识别结果 ===")
        print(f"识别文本内容:\n{result['result']}")
        print(f"文本长度: {len(result['result'])} 字符")
        print("==================\n")

    def test_invalid_image_data(self):
        """测试无效的图片数据"""
        # 准备无效的图片数据
        invalid_image_data = b"invalid image data"
        
        # 发送请求
        response = requests.post(
            f"{self.base_url}/image",
            data=invalid_image_data,
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400, "对于无效的图片数据应该返回400错误")
        result = response.json()
        self.assertIn("detail", result, "错误响应中应包含detail字段")

    def test_empty_image_data(self):
        """测试空的图片数据"""
        # 发送请求
        response = requests.post(
            f"{self.base_url}/image",
            data=b"",
            headers=self.headers
        )
        
        self.assertEqual(response.status_code, 400, "对于空的图片数据应该返回400错误")
        result = response.json()
        self.assertIn("detail", result, "错误响应中应包含detail字段")

if __name__ == '__main__':
    unittest.main()