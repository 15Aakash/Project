import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_tailored_resume_points(resume_text, job_description):

    prompt = f"""
You are an expert ATS resume writer.

Based on the resume and job description, generate tailored resume improvements.

Rules:
- Do not invent fake experience
- Use only skills/projects from the resume
- Make bullets ATS-friendly
- Focus on measurable impact
- Keep bullets professional

Return:

1. Tailored Professional Summary
2. Tailored Skills Section
3. Improved Experience Bullets
4. Improved Project Bullets

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