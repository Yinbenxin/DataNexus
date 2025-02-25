import requests
import json
import time

# 创建mask任务
url = "http://127.0.0.1:8000/api/v1/mask"

# 准备请求数据
data = {
    "text": "张三的手机号是18063218951，李四的手机号是19099099090， 王五的手机号是18063218951",
    "mask_type": "similar",
    "mask_model": "paddle",
    "mask_field": ["张三", "李四", "王五"]
}

# 发送POST请求
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=data, headers=headers)
print("创建任务响应：")
print(response.text)

# # 解析响应获取task_id
task_data = json.loads(response.text)
print(task_data)
task_id = task_data["task_id"]

# 查询任务状态和结果
url = f"http://127.0.0.1:8000/api/v1/mask/{task_id}"

# 循环查询直到任务完成
while True:
    response = requests.get(url)
    result = json.loads(response.text)
    print("\n当前任务状态：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result["status"] in ["completed", "failed"]:
        break
    
    time.sleep(1)  # 每秒查询一次状态