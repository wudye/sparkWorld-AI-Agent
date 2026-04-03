from http.client import responses

from openai import OpenAI
from pydantic import BaseModel, Field

class SplitTask(BaseModel):
    task_count: int = Field(..., gt=0, lt=10, description="The number of sub-tasks to split.")
    tasks: list[str] = Field(..., description="The list of sub-tasks.")

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

system_prompt = """
You are a helpful assistant that splits a complex task into several sub-tasks. 
When you receive a complex task, you will split it into 2 to maximus 10 sub-tasks and return the result in the following JSON format:
example:
what is today's weather of Vienna?
{
    "task_count": 3
    "tasks": ["search for today's weather in Vienna", "summarize the weather information", "answer the question based on the summarized information"]
}
"""

while True:
    user_prompt = input("Please enter a complex task (or 'exit' to quit): ").strip()
    if user_prompt == "exit":
        break

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    responses = client.chat.completions.create(
        model="llama3.1:8b",
        messages=messages,
        response_format={"type": "json_object"}
    )

    split_task = SplitTask.model_validate_json(responses.choices[0].message.content)
    print(f"Task count: {split_task.task_count}")
    for i, taks in enumerate(split_task.tasks, 1):
        print(f"Sub-task {i}: {taks}")