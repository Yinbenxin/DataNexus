import requests
import json

headers = {
    "Content-Type": "application/json"
}

url = "http://ocr.k8s.trustbe.net/v1/pdf_text"
pdf_url="http://bidding.fgw.hunan.gov.cn/ztbPdf/project/2024-05/noticeFile/Z430300H485H00212001/e53fe209820b481fa74cf83eb359ff1a.pdf"
params = {
    "pdf_url": pdf_url
}

r = requests.post(url, json=params)
print(r.text)

from pandasai import SmartDataframe
from pandasai.llm import OpenAI

llm = OpenAI(api_token="my-openai-api-key")
pandas_ai = SmartDataframe("data.csv", config={"llm": llm})

