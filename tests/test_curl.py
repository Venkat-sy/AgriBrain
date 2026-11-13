import requests
import json

url = "http://127.0.0.1:8002/api/v1/chat/troubleshoot"
data = {
    "session_id": "test-1",
    "user_question": "My rice crop has yellow leaves, what should I do?"
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")