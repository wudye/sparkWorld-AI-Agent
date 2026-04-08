import asyncio
from langchain_ollama import ChatOllama
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langgraph.prebuilt import create_react_agent  # ← 保持这里不变
from playwright.async_api import async_playwright


async def run_weather_agent():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()

        llm = ChatOllama(model="llama3.1:8b", temperature=0)  # ✅ 换更强的模型

        agent_executor = create_react_agent(model=llm, tools=tools)

        task = "Search Google for 'Vienna weather' and tell me the current temperature."
        result = await agent_executor.ainvoke({"messages": [("human", task)]})

        print(f"\nFinal Result: {result['messages'][-1].content}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_weather_agent())

"""

import asyncio
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain.agents import create_react_agent
from langchain_openai import ChatOpenAI
from playwright.async_api import async_playwright


async def run_weather_agent():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()

        # 用 DeepSeek API（比本地8B模型强很多）
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key="sk-your-deepseek-key",   # https://platform.deepseek.com/
            base_url="https://api.deepseek.com/v1",
            temperature=0.0,
        )

        agent_executor = create_react_agent(
            model=llm,
            tools=tools,
        )

        task = "Search Google for 'Vienna weather' and tell me the current temperature."
        
        result = await agent_executor.ainvoke(
            {"messages": [("human", task)]}
        )
        print(f"\nFinal Result: {result['messages'][-1].content}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_weather_agent())

"""