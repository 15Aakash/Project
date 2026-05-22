import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_recruiter_message(resume_text, job_description):

    prompt = f"""
You are a professional career assistant.

Write a short LinkedIn recruiter message for this job.

Rules:
- Under 120 words
- Friendly and professional
- Mention relevant skills from resume
- Ask politely about the opportunity
- Do not exaggerate

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