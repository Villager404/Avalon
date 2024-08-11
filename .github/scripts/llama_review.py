import requests
import json

optimization_prompt = """
Act as a seasoned programmer with over 20 years of commercial experience.
You must answer in Korean. 
Analyze the provided "{piece_of_code}" that is causing a specific "error". 
Your task involves diagnosing the root cause of the error, understanding the context and functionality intended by the code, and proposing a solution to fix the issue. 
Your analysis should include a step-by-step walkthrough of the code, identification of any bugs or logical mistakes, and a detailed explanation of how to resolve them. 
Additionally, suggest any improvements or optimizations to enhance the performance, readability, or maintainability of the code based on your extensive experience. 
Ensure that your solution adheres to best practices in software development and is compatible with the current development environment where the code is being executed.
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

def review_code(piece_of_code: str) -> str:
    url = "http://localhost:11434/api/generate"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "llama3",
        "prompt": optimization_prompt.replace("{piece_of_code}", piece_of_code)
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        exit(0)

    return parse_json_response(response)
