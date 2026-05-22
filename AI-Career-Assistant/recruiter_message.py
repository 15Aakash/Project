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

Write a short LinkedIn outreach message from the candidate to a recruiter or hiring manager.

Important:
- The candidate is applying or showing interest.
- Do NOT write as if the recruiter is contacting the candidate.
- Start with: Hi [Recruiter Name],
- Keep it under 120 words.
- Mention relevant skills from the resume.
- Mention interest in the role/company.
- Ask politely to connect or discuss the opportunity.
- End with: Best regards, Aakash Kathirvel
- Do not invent experience.

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
