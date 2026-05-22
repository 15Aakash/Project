import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def career_chatbot_response(resume_text, user_question):
    prompt = f"""
You are an AI Career Coach.

Use the resume below to answer the user's career question.

Rules:
- Be practical
- Give clear steps
- Do not exaggerate
- Keep answer helpful and career-focused

Resume:
{resume_text}

User Question:
{user_question}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text