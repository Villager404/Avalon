import requests
import json

optimization_prompt = """
Please review the following code with a focus on optimization, code style, runtime error. 
If there are areas where performance can be improved, provide specific suggestions and explain the reasons. 
If you have recommended code changes, include them between ``` and ``` for clarity. 
If there are no optimizations needed or if the potential improvements are negligible, simply respond with 'Nothing'. 
Please keep your review within 30 lines."
"""

code = """
internal class BinarySearch
    {
        public static int Search(int[] array, int target)
        {
            int left = 0;
            int right = array.Length - 1;

            while (left <= right)
            {
                int mid = left + (right - left) / 2;

                // Check if target is present at mid
                if (array[mid] == target)
                    return mid;

                // If target greater, ignore left half
                if (array[mid] < target)
                    left = mid + 1;

                // If target is smaller, ignore right half
                else
                    right = mid - 1;
            }

            // If we reach here, the element was not present
            return -1;
        }
    }
"""

url = "http://localhost:11434/api/generate"
data = {
    "model": "llama3",
    "prompt": optimization_prompt + "\n" + code
}

headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print('Success')
else:
    print("Error:", response.status_code, response.text)
    exit(0)

json_objects = response.content.decode().strip().split("\n")

# 각 JSON 객체를 Python 사전으로 변환
data = [json.loads(obj) for obj in json_objects]
res_text = ''
# 변환된 데이터 출력
for item in data:
    res_text += item['response']

print(res_text)