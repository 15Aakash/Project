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

Based on the resume and job description, generate a final interview preparation document.

Include:

1. Technical Interview Questions
2. Behavioral Interview Questions
3. Resume-Based Questions
4. Suggested Answers Summary

Rules:
- Keep answers concise and professional.
- Do not include conversational filler.
- Do not say "Certainly".
- Do not end with "If you want..." or offer extra follow-up actions.
- Do not mention that you can generate more content later.
- The output should be a complete standalone interview preparation document.
- Use clean headings and bullet points.

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
