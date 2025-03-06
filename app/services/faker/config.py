import numpy as np


# faker库支持的类型
FAKER_TYPES_MAP = {
    '姓名': 'name',
    '电话号码': 'phone_number',
    '出生日期': 'date_of_birth',
    '地址': 'address',
    '省份': 'province',
    '城市': 'city',
    '街道名称': 'street_name',
    '公司': 'company',
    '工作': 'job',
    '电子邮件': 'email',
    '域名': 'domain_name',
    '信用卡号码': 'credit_card_number',
    '车牌号码': 'license_plate',
    '密码': 'password',
    '区县': 'district',
    '纬度': 'latitude',
    '经度': 'longitude',
    '日期': 'date',
    '时间': 'time',
}

# 其他类型映射，新增类型需要在该字典中添加，并在faker_data中添加对应的json文件
OTHER_TYPE_MAP={
    '民族': 'ethnicity',
    '宗教信仰': 'religions',
    '政治身份': 'political_identities',
    '政府部门': 'government_departments',
}


