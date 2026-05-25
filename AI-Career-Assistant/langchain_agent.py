import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


def langchain_route_request(user_request):

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a LangChain-based AI agent router.

Route the user request to exactly one agent:

ATS_AGENT
RESUME_TAILOR_AGENT
COVER_LETTER_AGENT
RECRUITER_AGENT
INTERVIEW_COACH_AGENT
MOCK_INTERVIEW_AGENT
CAREER_COACH_AGENT
TRACKER_AGENT
AUTONOMOUS_WORKFLOW_AGENT

Return only the agent name.
"""
            ),
            (
                "human",
                "{user_request}"
            )
        ]
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "user_request": user_request
        }
    )

    return response.content.strip()
