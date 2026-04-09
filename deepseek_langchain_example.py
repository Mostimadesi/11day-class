import os
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def call_deepseek_with_langchain(
    #配置基本参数
    prompt: str,
    api_key: Optional[str] = None,
    model: str = "deepseek-chat",
    base_url: str = "https://api.deepseek.com/v1",
) -> str:
    """Call DeepSeek with LangChain and return the text response."""
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY")  #从环境变量获取API密钥
    if not api_key:
        raise ValueError("Please pass api_key or set DEEPSEEK_API_KEY.")

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
    )

    response = llm.invoke(
        [
            #设置系统提示词
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt),
        ]
    )

    return response.content if isinstance(response.content, str) else str(response.content)


if __name__ == "__main__":
    prompt = input("Please enter your prompt: ")
    result = call_deepseek_with_langchain(prompt)
    print(result)
