import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_tools import career_tools

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a career AI tool-calling agent.

Your job is to choose the best available tool based on the user's request.

Use exactly one tool.

Return only the tool result.
"""
        ),
        (
            "human",
            "{input}"
        ),
        MessagesPlaceholder(
            variable_name="agent_scratchpad"
        )
    ]
)

agent = create_openai_tools_agent(
    llm,
    career_tools,
    prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=career_tools,
    verbose=True
)


def run_langchain_tool_agent(user_request):

    result = agent_executor.invoke(
        {
            "input": user_request
        }
    )

    return result["output"]
