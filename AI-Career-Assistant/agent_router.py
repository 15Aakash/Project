import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def route_user_request(user_request):

    prompt = f"""
You are an AI agent router.

Classify the user's request into exactly one of these agents:

ATS_AGENT
RESUME_TAILOR_AGENT
COVER_LETTER_AGENT
RECRUITER_AGENT
INTERVIEW_COACH_AGENT
MOCK_INTERVIEW_AGENT
CAREER_COACH_AGENT
TRACKER_AGENT

Rules:
- Return only the agent name.
- Do not explain.
- Choose the best matching agent.

User Request:
{user_request}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return response.output_text.strip()
