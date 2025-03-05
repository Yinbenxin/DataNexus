from app.services.info_extract.info_extractor import InfoExtractor

def test_info_extraction():
    # 创建示例文本，包含各种需要提取的信息
    sample_text = """
    张三的身份证号码是330102199001015678，
    出生日期是1990年01月01日，
    属于汉族。
    他的护照号码是E88888888，
    手机号是13912345678，
    电子邮件是zhangsan@example.com。
    """

    # 创建信息提取器实例
    extractor = InfoExtractor()

    # 提取所有信息
    results = extractor.extract_all(sample_text)

    # 打印提取结果
    print("提取结果：")
    for info_type, info_list in results.items():
        print(f"{info_type}: {info_list}")

def test_info_extraction_by_type():
    # 创建示例文本
    sample_text = """
    张三的身份证号码是330102199001015678，
    出生日期是1990年01月01日，
    属于汉族。牛三金是他的好朋友，和陈鑫是他的同学。甘露也是我们的朋友。
    他的护照号码是E88888888，
    手机号是13912345678，
    电子邮件是zhangsan@example.com。
    """

    # 创建信息提取器实例
    extractor = InfoExtractor()

    # 测试单类型提取
    single_type_result = extractor.extract_by_type(sample_text, '身份证号')
    print("\n单类型提取结果：")
    print(f"身份证号: {single_type_result}")

    # 测试多类型同时提取
    multi_types = ['出生日期', '民族', '手机号', '电子邮件', '姓名']
    multi_type_results = extractor.extract_by_type(sample_text, multi_types)
    print("\n多类型提取结果：")
    print(f"提取到的信息: {multi_type_results}")


if __name__ == '__main__':
    test_info_extraction()
    test_info_extraction_by_type()