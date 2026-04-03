import json
import os
import dotenv
import requests

"""
for only streaming 
dotenv.load_dotenv()
with requests.request(
    "POST",
    "https://api.deepseek.com/v1/stream",
    headers={
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-llm-7b-base",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
        ],
        "stream": True,
    },
) as resp:
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            if line.startswith("data: "):
                print(line[6:])
                
                
response = requests.request(
    "POST",
    "https://api.deepseek.com/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "你好，你是?"}
        ],
        "stream": False
    }
)


"""
"""
no streaming
url = "http://localhost:11434/api/chat"

payload = {
    "model": "deepseek-r1:8b",
    "messages": [
        {"role": "system","content": "You are a helpful assistant."},
        {"role": "user","content": "What is the capital of France?"}
    ],
    "stream": False
}

resp = requests.post(url, json=payload)
resp.raise_for_status()
data = resp.json()
print(data)
print(data["message"]["content"])

"""

url = "http://localhost:11434/api/chat"

payload = {
    "model": "deepseek-r1:8b",
    "messages": [
        {"role": "system","content": "You are a helpful assistant."},
        {"role": "user","content": "What is the capital of France?"}
    ],
    "stream": True
}

"""
data = {
    "model": "deepseek-r1:8b",
    "created_at": "...",
    "message": {
        "role": "assistant",
        "content": "",          # always empty here
        "thinking": " user"     # or " is", " asking", ...
    },
    "done": False
}

"""
with requests.post(url,json=payload) as resp:
    """
    Checks the HTTP status code:
    If it’s 2xx (200–299): does nothing, returns None.
    If it’s 4xx or 5xx: raises an exception requests.HTTPError.
    """
    resp.raise_for_status()
    for line in resp.iter_lines(decode_unicode=True):
        if  not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            continue
        # print(data.get("message", {}).get("content", ""))
        print(data)
        chunk = data.get("message", {}).get("content", "")
        if chunk:
            print(chunk, end="", flush=True)
        if data.get("done"):
            break

