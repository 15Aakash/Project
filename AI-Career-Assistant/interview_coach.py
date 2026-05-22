import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_interview_questions(resume_text, job_description):

    prompt = f"""
You are an AI interview coach.

Based on the resume and job description:

Generate:

1. Technical Interview Questions
2. Behavioral Questions
3. Resume-based Questions
4. Suggested Answers

Keep the answers concise and professional.

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text