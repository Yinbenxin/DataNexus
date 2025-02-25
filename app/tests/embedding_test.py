# 请求测试
# 端口： 0.0.0.0:8000/api/v1/embedding/
# 请求方式：POST
# 请求参数：
# text: 你好，世界！
# 返回值：
# {
#     "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# }
import requests

url = "http://127.0.0.1:8000/api/v1/embedding/"

tesk_id = "ea7f73ca-538f-486b-942a-ce08a9b46023"

response = requests.get(url+ tesk_id)




print(response.text)
