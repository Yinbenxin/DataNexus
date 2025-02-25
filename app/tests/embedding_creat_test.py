import requests
import json
import time

# 创建embedding任务
url = "http://127.0.0.1:8000/api/v1/embedding"

params = {
    "text": "2edca33b-dad9-49c3-a441-e5672d6b1429"
}

response = requests.post(url, params=params)
print("创建任务响应：")
print(response.text)

# 解析响应获取task_id
task_data = json.loads(response.text)
task_id = task_data["task_id"]

# 查询任务状态和结果
url = f"http://127.0.0.1:8000/api/v1/embedding/{task_id}"

# 循环查询直到任务完成
while True:
    response = requests.get(url)
    result = json.loads(response.text)
    print("\n当前任务状态：")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result["status"] in ["completed", "failed"]:
        break
    
    time.sleep(10)  # 等待1秒后再次查询