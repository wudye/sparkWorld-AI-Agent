import json
from logging import root

from huggingface_hub.cli.inference_endpoints import resume
from openai import OpenAI

def calculator(expression: str) -> str:
    """a simple calculator tool demo"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {e}"})

class ReActAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )
        self.model ="llama3.1:8b"
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant. You can use the calculator tool to answer math questions. When you want to use the tool, respond with a message like this: {\"tool\": \"calculator\", \"input\": \"2 + 2\"}. If you do not know how to answer a question,  just answer I don't know."}
        ]
        self.available_tools = {"calculator": calculator}
        self.tool = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "A simple calculator tool that evaluates basic math expressions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The math expression to evaluate, e.g., '2 + 2'."
                            }
                        }
                    },
                    "required": ["expression"]
                }
            }
        ]

    def process_query(self, query: str) -> str:
        self.messages.append({
            "role": "user",
            "content": query
        })
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        # model response adds to the history messages
        self.messages.append(response_message.model_dump())

        if tool_calls:
            for tool_call in tool_calls:
                print("tool call", tool_call.function.name)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                function_to_all = self.available_tools[tool_name]

                # execute the tool function with the provided arguments and get the result
                result = function_to_all(**tool_args)
                print(f"tool [{tool_name}] result: {result}")
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

            """
            Do not call any tools this time. Just read the conversation 
            (including the tool results I’ve already added) and answer directly.
            """
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tool,
                tool_choice="none"
            )
            self.messages.append(second_response.choices[0].message.model_dump())
            return "Assistant: " + second_response.choices[0].message.content
        else:
            return response_message.content

    def chat_loop(self):
        while True:
            try:
                query = input("\nQuery:").strip()
                if query.lower() == "quit":
                    break
                print(self.process_query(query))
            except Exception as e:
                print(f"Error: {e}")






if __name__ == "__main__":
    ReActAgent().chat_loop()