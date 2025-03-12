from langchain_openai import OpenAI
from langchain.schema import HumanMessage

llm = OpenAI(
    openai_api_key="sk-Wn6YCAFpDZ9LlW0m4NJ54wHSAQ4PlzKqVSI6v78cvcTl90Kd",
    base_url="https://api.chatanywhere.tech/v1/chat",
    model= "gpt-4"
)

llm = OpenAI(
    openai_api_key="a3b5377fa9d3585c8094f63a5625fcdf.MKWblaO3GY1o7bko",
    base_url="https://open.bigmodel.cn/api/paas/v4/chat",
    model= "glm-4-flash"
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},  # 系统消息
    {"role": "user", "content": "什么是LangChain？它如何在AI应用中使用？"}  # 用户消息
]
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 调用 OpenAI 模型
#response = llm.run("什么是LangChain？它如何在AI应用中使用？")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是世界级的技术文档作者。"),
    ("user", "{input}")
])
chain = prompt | llm
chain.invoke({"input": "langsmith如何帮助测试?"})
#response = llm.invoke(input=messages)

#llm.invoke()
#print(response)
import os
import pandas as pd
from pandasai import Agent

employees_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Name": ["John", "Emma", "Liam", "Olivia", "William"],
    "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
}

salaries_data = {
    "EmployeeID": [1, 2, 3, 4, 5],
    "Salary": [5000, 6000, 4500, 7000, 5500],
}

employees_df = pd.DataFrame(employees_data)
salaries_df = pd.DataFrame(salaries_data)


# By default, unless you choose a different LLM, it will use BambooLLM.
# You can get your free API key signing up at https://pandabi.ai (you can also configure it in your .env file)
os.environ["PANDASAI_API_KEY"] = "$2a$10$BiTjcJsblZJ.4zvDPbhbqOGsy2IrD6Gwjke7tMQGSrArW8bOGWCFe"

agent = Agent([employees_df, salaries_df], memory_size=10)

query = "Who gets paid the most?"

# Chat with the agent
response = agent.chat(query)
print(response)

# Get Clarification Questions
questions = agent.clarification_questions(query)

for question in questions:
    print(question)

# Explain how the chat response is generated
response = agent.explain()
print(response)