
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
import json


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
                "content": "You are a helpful assistant. You can use the calculator tool to answer math questions. When you want to use the tool, respond with a message like this: {\"tool\": \"calculator\", \"input\": \"2 + 2\"}. If you do not know how to answer a question, just answer I don't know."
            }
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
            tools=self.tool,
            stream=True
        )

        is_tool_calls = False
        content = ""
        tool_calls_obj: dict[str, ChoiceDeltaToolCall] = {}

        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            """
            Choice(delta=ChoiceDelta(content='', function_call=None, refusal=None, 
            role='assistant', tool_calls=[ChoiceDeltaToolCall(index=0, id='call_2kvxcppd', 
            function=ChoiceDeltaToolCallFunction(arguments='{"expression":"100 + 300"}',
             name='calculator'), type='function')]), finish_reason=None, index=0, logprobs=None)
            """
            chunk_tool_calls = chunk.choices[0].delta.tool_calls

            if chunk_content:
                content += chunk_content
            if chunk_tool_calls:
                for chunk_tool_call in chunk_tool_calls:
                    if tool_calls_obj.get(chunk_tool_call.index) is None:
                        tool_calls_obj[chunk_tool_call.index] = chunk_tool_call
                    else:
                        tool_calls_obj[chunk_tool_call.index].function.arguments += chunk_tool_call.function.arguments


            if chunk_content:
                print(chunk_content, end="", flush=True)

            if is_tool_calls is False:
                if chunk_tool_calls:
                    is_tool_calls = True

        tool_calls_json = [tool_call for tool_call in tool_calls_obj.values()]

        self.messages.append(
            {
                "role": "assistant",
                "content": content if content != "" else None,
                "tool_calls": tool_calls_json if tool_calls_json else None
            }
        )

        if  is_tool_calls:
            for tool_call in tool_calls_json:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                function_to_all = self.available_tools[tool_name]

                # execute the tool function with the provided arguments and get the result
                result = function_to_all(**tool_args)
                print(f"\nTool [{tool_name}] result: {result}")
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_name,
                    "content": result
                })

                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool,
                    tool_choice="none",
                    stream=True
                )
                print("\nAssistant is thinking...",  end="", flush=True)
                for chunk in second_response:
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content:
                        print(chunk_content, end="", flush=True)

        print("\n--- End of response ---")

    def chat_loop(self):
        while True:
            try:
                query = input("\nQuery:").strip()
                if query.lower() == "quit":
                    break
                self.process_query(query)
            except Exception as e:
                print(f"Error: {e}")
                break


if __name__ == "__main__":
    agent = ReActAgent()
    agent.chat_loop()