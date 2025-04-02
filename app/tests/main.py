from faker import Faker

# 初始化 Faker，并指定语言为中文
fake = Faker('zh_CN')

# 生成随机身份证号
id_card_number = fake.company_email_domain()
print("随机身份证号:", id_card_number)