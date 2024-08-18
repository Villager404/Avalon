import requests
import json

description_prompt = """
Act as a seasoned programmer with over 20 years of commercial experience. 
Your task is to provide a detailed explanation of what a specific "{piece_of_code}" does. 
You must answer in Korean.
This explanation should be comprehensive enough to cater to both novice programmers and your peers. 
Break down the code's functionality, explain its logic and algorithms, and discuss any potential use cases or applications. 
Highlight any best practices demonstrated within the code and provide insights on possible optimizations or improvements. 
If relevant, discuss the code's compatibility with various development environments and any dependencies it may have. 
Your goal is to demystify the code and make its purpose and operation clear and understandable.
All answers must be in Korean.
"""

correctness_prompt = """
Act as a seasoned programmer with over 20 years of commercial experience. 
Analyze the provided "{piece_of_code}" that is causing a specific "error".
You must answer in Korean. 
Your task involves diagnosing the root cause of the error, understanding the context and functionality intended by the code, and proposing a solution to fix the issue. 
Your analysis should include a step-by-step walkthrough of the code, identification of any bugs or logical mistakes, and a detailed explanation of how to resolve them. 
Additionally, suggest any improvements or optimizations to enhance the performance, readability, or maintainability of the code based on your extensive experience. 
Ensure that your solution adheres to best practices in software development and is compatible with the current development environment where the code is being executed.
All answers must be in Korean.
"""

maintainability_prompt = """
As a seasoned programmer with over 20 years of commercial experience, your task is to perform a comprehensive code review on the provided "{piece_of_code}".
You must answer in Korean. 
Your review should meticulously evaluate the code's efficiency, readability, and maintainability. 
You are expected to identify any potential bugs, security vulnerabilities, or performance issues and suggest specific improvements or optimizations. 
Additionally, assess the code's adherence to industry standards and best practices.
Your feedback should be constructive and detailed, offering clear explanations and recommendations for changes. 
Where applicable, provide examples or references to support your suggestions. 
Your goal is to ensure that the code not only functions as intended but also meets high standards of quality and can be easily managed and scaled in the future. 
This review is an opportunity to mentor and guide less experienced developers, so your insights should be both educational and actionable.
All answers must be in Korean.
"""

def parse_json_response(response) -> str:
    json_objects = response.content.decode().strip().split("\n")

    # 각 JSON 객체를 Python 사전으로 변환
    data = [json.loads(obj) for obj in json_objects]
    res_text = ''
    # 변환된 데이터 출력
    for item in data:
        res_text += item['response']

    return res_text

def review_code(prompt: str, piece_of_code: str) -> str:
    url = "http://host.docker.internal:11434/api/generate"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3",
        "prompt": prompt.replace("{piece_of_code}", piece_of_code)
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        exit(0)

    return parse_json_response(response)

def review_code_for_description(piece_of_code: str) -> str:
    return review_code(description_prompt, piece_of_code)

def review_code_for_correctness(piece_of_code: str) -> str:
    return review_code(correctness_prompt, piece_of_code)

def review_code_for_maintainability(piece_of_code: str) -> str:
    return review_code(maintainability_prompt, piece_of_code)
