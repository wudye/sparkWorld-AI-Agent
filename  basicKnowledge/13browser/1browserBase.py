import asyncio
from browser_use import Agent, Browser, ChatGroq, ChatOllama  # ✅ 用 browser_use 自带的
import dotenv
import os


dotenv.load_dotenv()

async def example():
    browser = Browser()
    """
    llm = ChatOllama(
        model="llama3.1:8b",
        host="http://localhost:11434",  # ✅ 注意：用 host 参数，不是 base_url
        # ollama_options={"temperature": 0.7},  # 可选：模型参数
    )
    """
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.0,  # 结构化输出建议设为0
    )

    agent = Agent(
        task="check Vienna current weather",
        llm=llm,
        browser=browser,
    )
    return await agent.run()


if __name__ == "__main__":
    asyncio.run(example())
