import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_cover_letter(resume_text, job_description):

    prompt = f"""
You are a professional career assistant.

Write a short cover letter based on the resume and job description.

Rules:
- Under 250 words
- Professional tone
- Do not exaggerate
- Use only resume-based experience
- Make it tailored to the job

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