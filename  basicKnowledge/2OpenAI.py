import dotenv
from openai import OpenAI
import base64

dotenv.load_dotenv()

# Point the OpenAI client to your local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # dummy key, Ollama ignores it
)

response = client.chat.completions.create(
    model="deepseek-r1:8b",  # your Ollama model name
    messages=[
        {"role": "user", "content": "What is the capital of France?"},
    ],
)
image_path = "./resource/tower.jpeg"
with open(image_path,"rb") as f:
    image_data = f.read()

image_url = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"

response = client.chat.completions.create(
    model="llava:7b",  # your Ollama model name
    messages=[
        {"role": "user",
         "content": [
             {"type": "text", "text": "explain this image"},
             {"type": "image_url", "image_url": {"url": image_url}}
         ]}
    ]
)


print(response.choices[0].message.content)
"""
dotenv.load_dotenv()
client = OpenAI(
    base_url="https://api.openai.com/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)  # uses OPENAI_API_KEY
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.choices[0].message.content)

"""