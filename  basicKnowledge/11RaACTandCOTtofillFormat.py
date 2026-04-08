import json
from openai import OpenAI
from openai.types.chat.chat_completion_chunk import ChoiceDeltaToolCall
from pydantic import BaseModel, Field
from datetime import  date
from typing import Literal

class GetEmployeeInfoInput(BaseModel):
    employee_id: str=Field(..., description="employee ID to query")

class SubmitReimbursementInput(BaseModel):
    employee_id: str = Field(..., description="employee id")
    employee_name: str = Field(..., description="employee name")
    submission_date: date = Field(..., description="submission date")
    trip_start_date: date = Field(..., description="start date of the business trip")
    trip_end_date: date = Field(..., description="end date of the business trip")
    destination: str = Field(..., description="the city of the business trip")
    transportation_cost: float = Field(..., description="transportation cost")
    accommodation_cost: float = Field(..., description="accommodation cost")
    meal_cost: float = Field(..., description="meal cost")
    total_cost: float = Field(..., description="total cost")
    reimbursement_level: Literal['standard', 'senior', 'VIP'] = Field(..., description="reimbursement level")


class CalculatorInput(BaseModel):
    expression: str = Field(..., description="math expression")


def get_employee_info(employee_id: str) -> str:
    """get employee info by employee id, for demo purpose, we only support one employee with id 123456"""
    print(f"-------get employee info for {employee_id}----")
    if employee_id == "123456":
        return json.dumps({ "name":" John Doe","level" : "Manager"})
    else:
        return json.dumps({"error": "employee not found"})

def submit_reimbursement(**kwargs) -> str:
    """submit reimbursement"""
    print(f"-------submit reimbursement for {kwargs}----")
    return json.dumps({"status": "success", "message": "reimbursement submitted successfully"})

def calculator(expression: str) -> str:
    """a simple calculator tool demo"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {e}"})
"""
Add the following new rule to our reimbursement policy: “If the total amount exceeds 2000 yuan and the employee’s rank is not ‘Director’, then the reimbursement level cannot be ‘VIP’.”
You only need to modify your System Prompt and then see whether the Agent can correctly apply this new rule during its second round of reasoning and adjust the final reimbursement level.
"""


SYSTEM_PROMPT_POLICY_VERSION = """
You are an intelligent corporate reimbursement assistant. Your task is to help employees fill in and submit business travel reimbursement forms based on the user’s request and the company’s reimbursement policies.

You must follow the following cycle pattern of Thinking and Acting (ReAct):

1. Thought
   - Review the goal: What is my current final goal? (For example: to fill in and submit a complete reimbursement form.)
   - Analyze the current situation: What information have I already obtained? What information is still missing?
   - Use CoT (Chain-of-Thought): Carefully read and apply the reimbursement policies step by step. For example, calculate the total amount, determine the reimbursement level, etc. Write your calculations and reasoning process in the Thought section.
   - Plan the next step: What should I do next? Should I query information, perform calculations, or prepare to submit?

2. Action
   - Based on your thinking, decide whether to call a tool or ask the user a question.
   - The tools you can use are: `get_employee_info`, `submit_reimbursement`, `calculator`.
   - If all information has been gathered and all calculations are complete, your final action should be to call the `submit_reimbursement` tool.
   - Before calling a tool, also output your thinking process; do not call tools directly to avoid causing a high-latency experience.

3. Company reimbursement policies
   - You must strictly follow these rules when determining and adjusting the reimbursement level:
     1) The reimbursement level is one of: "standard", "senior", "VIP".
     2) After you have calculated the total_cost and obtained the employee's level from get_employee_info, you MUST check the following rule BEFORE submitting:
        - If the total reimbursement amount (total_cost) is greater than 2000 (currency units), AND the employee level is NOT "Director" (or an equivalent high-level title), THEN the reimbursement_level CANNOT be "VIP".
        - In that case, you MUST downgrade the reimbursement level to a suitable non-VIP level (e.g. "standard" or "senior"), and clearly explain in your thought that you are applying this policy rule.
     3) If the total_cost is less than or equal to 2000, or the employee level is "Director", then the reimbursement_level may be "VIP" as long as it is consistent with the other policies.

When you perform your SECOND reasoning step (after tools have been called and you have access to total_cost and employee level), you MUST:
   - Re-check the above policy rule.
   - If the user or previous reasoning suggested a "VIP" level that violates the rule, you MUST correct it to a compliant level and then call `submit_reimbursement` with the corrected reimbursement_level.

Please begin your work.
"""


SYSTEM_PROMPT = """
    You are an intelligent corporate reimbursement assistant. Your task is to help employees fill in and submit business travel reimbursement forms based on the user’s request and the company’s reimbursement policies.
    
    You must follow the following cycle pattern of Thinking and Acting (ReAct):
    
    1. Thought
       - Review the goal: What is my current final goal? (For example: to fill in and submit a complete reimbursement form.)
       - Analyze the current situation: What information have I already obtained? What information is still missing?
       - Use CoT (Chain-of-Thought): Carefully read and apply the reimbursement policies step by step. For example, calculate the total amount, determine the reimbursement level, etc. Write your calculations and reasoning process in the Thought section.
       - Plan the next step: What should I do next? Should I query information, perform calculations, or prepare to submit?
    
    2. Action
       - Based on your thinking, decide whether to call a tool or ask the user a question.
       - The tools you can use are: `get_employee_info`, `submit_reimbursement`, `calculator`.
       - If all information has been gathered and all calculations are complete, your final action should be to call the `submit_reimbursement` tool.
       - Before calling a tool, also output your thinking process; do not call tools directly to avoid causing a high-latency experience.
    
    Please begin your work.
    """


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
                "content": SYSTEM_PROMPT
            }
        ]
        self.available_tools = {
            submit_reimbursement.__name__: {"tool": submit_reimbursement,"input": SubmitReimbursementInput},
            get_employee_info.__name__: {"tool": get_employee_info, "input": GetEmployeeInfoInput},
            calculator.__name__: {"tool": calculator, "input": CalculatorInput},
        }

        self.tools = [{
            "type": "function",
            "function": {
                "name": tool["tool"].__name__,
                "description": tool["tool"].__doc__,
                "parameters": tool["input"].model_json_schema()

            }
        } for tool in self.available_tools.values()]

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

        for chunck in response:
            chunck_content = chunck.choices[0].delta.content
            chunck_tool_calls = chunck.choices[0].delta.tool_calls

            if chunck_content:
                content += chunck_content

            if chunck_tool_calls:
                for chunk_tool_call in chunck_tool_calls:
                    if tool_calls_obj.get(chunk_tool_call.index) is None:
                        tool_calls_obj[chunk_tool_call.index] = chunk_tool_call
                    elif chunk_tool_call.function.arguments is not None:
                        tool_calls_obj[chunk_tool_call.index].function.arguments += chunk_tool_call.function.arguments

            if chunck_content:
                print(chunck_content, end="", flush=True)

            if is_tool_calls is False:
                if chunck_tool_calls:
                    is_tool_calls = True

        tool_calls_json = [tool_call for tool_call in tool_calls_obj.values()]

        self.messages.append({
            "role": "assistant",
            "content": content if content != "" else None,
            "tool_calls": tool_calls_json if tool_calls_json else None
        })

        if is_tool_calls:
            for tool_call in tool_calls_json:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                function_to_call = self.available_tools[tool_name]["tool"]

                try:
                    inputs = self.available_tools[tool_name]["input"].model_validate(tool_args)
                    result = function_to_call(**inputs.model_dump())
                except Exception as e:
                    result = (f"Error: {e}")

                print(f"Tool {tool_name} returned: {result}")
            self.messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": result
            })

        self.process_query(result)
        print("\n")

    def chat_loop(self):
        while True:
            try:
                query = input("\nQuery:")
                if query.lower() == "quit":
                    print("Exiting chat.")
                    break
                self.process_query(query)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    ReActAgent().chat_loop()
