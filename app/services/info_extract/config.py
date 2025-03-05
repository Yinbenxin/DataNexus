# 支持的信息类型及其正则表达式模式
FIXED_TYPES = {
    # 15位或18位身份证号码
    '身份证号': r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]|[1-9]\d{7}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}',
    # 支持多种日期格式（年月日）
    '出生日期': r'(?:19|20)\d{2}[-/年.](?:0?[1-9]|1[0-2])[-/月.](?:0?[1-9]|[12]\d|3[01])日?',
    # 中国各民族名称
    '民族': r'[汉满蒙回藏维维吾尔壮苗彝傣藏傈僳佤拉祜布朗白纳西哈尼黎傣景颇达斡尔仫佬东乡撒拉毛南仡佬锡伯柯尔克孜土家土哈萨克俄罗斯鄂温克德昂保安裕固京族塔塔尔独龙族鄂伦春族赫哲族门巴族珞巴族基诺族]族',
    # 护照或其他11位数字证件号
    '证件号码': r'(?:[A-Z][0-9]{8}|(?<![0-9])[0-9]{11}(?![0-9]))',
    # 中国大陆手机号码
    '手机号': r'(?<!\d)1[3-9]\d{9}(?!\d)',
    # 电子邮件地址
    '电子邮件': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    # 16-19位银行卡号
    '银行卡号': r'(?<![0-9])(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})(?![0-9])',
    # 支持新能源和普通车牌
    '车牌号': r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-HJ-NP-Z0-9]{4}[A-HJ-NP-Z0-9挂学警港澳]|[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][0-9]{5}[DF]',
    # 5-11位QQ号码
    'QQ号码': r'(?<![0-9])[1-9][0-9]{4,10}(?![0-9])',
    # 6-20位字母数字下划线
    '微信号': r'[a-zA-Z][a-zA-Z0-9_-]{5,19}',
    # 18位统一社会信用代码
    '统一社会信用代码': r'[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}',
    # 6位邮政编码
    '邮政编码': r'(?<![0-9])\d{6}(?![0-9])',
    # 支持IPv4和IPv6地址
    'IP地址': r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
    # 支持冒号或连字符分隔的MAC地址
    'MAC地址': r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}'
}

# 类型转换映射
CONVERT_MAP = {
    '姓名': '人名',
    '人物': '人名',
}