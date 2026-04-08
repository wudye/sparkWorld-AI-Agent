import  json
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall


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
        self.model = "gemma4:e2b"
        self.messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant. You can  answer any questions, but you must follow this rules strictly to answer the questions:"
                        1. Inside the <think> tag, show your thinking process in detail: break the problem down into multiple steps and carry out the reasoning and calculations step by step.
                        2.Inside the <answer> tag, provide only the final, clear answer.
                        Make sure your answer does not contain any extra text outside the <think> and <answer> tags.
                           """
            }
        ]

        self.available_tools = {"calculator": calculator}
        self.tools = [
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
                        },
                        "required": ["expression"]
                    }
                }
            }
        ]

    def process_query(self, query: str) -> None:
        self.messages.append({"role": "user", "content": query})
        print("Assistant is thinking...",  end="", flush=True)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools,
            stream=True
        )

        is_tool_calls = False
        content = ""
        tool_calls_obj: dict[str, ChoiceDeltaToolCall] = {}

        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            chunk_tool_calls = chunk.choices[0].delta.tool_calls

            if chunk_content:
                content += chunk_content
            if chunk_tool_calls:
                for chunk_tool_call in chunk_tool_calls:
                    if tool_calls_obj.get(chunk_tool_call.index) is None:
                        tool_calls_obj[chunk_tool_call.index] = chunk_tool_call
                    elif chunk_tool_call.function.arguments is not None:
                        tool_calls_obj[chunk_tool_call.index].function.arguments += chunk_tool_call.function.arguments


            if chunk_content:
                print(chunk_content, end="", flush=True)

            if is_tool_calls is False:
                if chunk_tool_calls:
                    is_tool_calls = True

        tool_calls_json = [tool_call for tool_call in tool_calls_obj.values()]

        self.messages.append({
            "role": "assistant",
            "content": content if content != "" else None,
            "tool_calls": tool_calls_json if tool_calls_json  else None
        })

        if is_tool_calls:
            for tool_call in tool_calls_json:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                function_to_call = self.available_tools[tool_name]

                result = function_to_call(**tool_args)
                print(f"tool [{tool_name}] result: {result}")
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                stream=True
            )

            for chunk in second_response:
                chunk_content = chunk.choices[0].delta.content

                if chunk_content:
                    print(chunk_content, end="", flush=True)
        print("\n")

    def chat_loop(self):
        while True:
            try:
                query = input("\nQuery:").strip()
                if query.lower() == "quit":
                    print("Exiting chat.")
                    break
                self.process_query(query)
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    agent = ReActAgent()
    agent.chat_loop()

