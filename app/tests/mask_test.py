import requests
import json
import time

# 创建mask任务
url = "http://127.0.0.1:8000/api/v1/mask"

# 准备请求数据
data = {
    "text": "2024年2月17日，李明在北京参加了第十届世界人工智能峰会。该活动由国际人工智能协会主办，并在国家会议中心举行。他在会上发表了一篇演讲，探讨了人工智能在金融领域的应用。他提到，根据《数字金融安全法》，银行应确保至少80%的交易符合安全标准。李明还展示了一款新型智能手机——XPhone Pro，其内置的语音助手能够用英语和法语进行自然交流。该手机目前售价为6999元人民币，较上一代价格降低了10%，首批限量1000台。此外，他还提到，未来五年内，亚洲地区将成为人工智能发展的核心市场。根据统计，目前已有超过300万名开发者投入该领域。他引用了一段来自《智能时代》一书的话，鼓励与会者迎接科技变革。当天的会议于下午3点结束，与会者们纷纷表示收获良多。会后，美国总统汤姆逊、法国总理托斯卡纳接见了李明。",
    "mask_type": "AES",
    "mask_model": "paddle",
    "mask_field": ["日期", '姓名', '职业', '地区', '外国人名', '时间']
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