import unittest
import os
from app.services.faker.faker import Faker
from app.services.faker.config import FAKER_TYPES_MAP, OTHER_TYPE_MAP

class TestFaker(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.faker = Faker()

    def test_generate_faker_types(self):
        """测试生成faker库支持的类型数据"""
        for zh_type, en_type in FAKER_TYPES_MAP.items():
            data = self.faker.generate(zh_type, 3)
            self.assertEqual(len(data), 3)
            self.assertTrue(all(isinstance(item, str) for item in data))

    def test_generate_other_types(self):
        """测试生成其他类型数据"""
        for zh_type in OTHER_TYPE_MAP.keys():
            data = self.faker.generate(zh_type, 3)
            self.assertEqual(len(data), 3)
            self.assertTrue(all(isinstance(item, str) for item in data))

    def test_generate_invalid_type(self):
        """测试生成无效类型数据"""
        data = self.faker.generate('invalid_type', 2)
        self.assertEqual(len(data), 2)
        # self.assertTrue(all(item == '[UNKNOWN_TYPE]' for item in data))

    def test_generate_invalid_count(self):
        """测试生成数据时使用无效的数量参数"""
        with self.assertRaises(ValueError):
            self.faker.generate('姓名', 0)
        with self.assertRaises(ValueError):
            self.faker.generate('姓名', -1)

    def test_generate_single_item(self):
        """测试生成单个数据项"""
        data = self.faker.generate('教师')
        print("data:", data)
        self.assertEqual(len(data), 1)
        self.assertTrue(isinstance(data[0], str))

if __name__ == '__main__':
    unittest.main()