
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-llm-7b-base")
tokenizer.save_pretrained("./resources/tokenizer")


# token
prompt = "hello, who are ?"
message = [{"role": "user", "content": "hello , calculate 123 * 321 "}]
print("prompt", len(tokenizer.encode(prompt)))
print(tokenizer.encode(prompt))
print("message", len(tokenizer.encode(message[0]["content"])))

from transformers import AutoTokenizer

chat_tokenizer_dir = "./resources/tokenizer"
token_local= AutoTokenizer.from_pretrained(chat_tokenizer_dir, local_files_only=True)

print("token_local", len(token_local.encode(prompt)))