import os
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_cover_letter(resume_text, job_description):

    today_date = date.today().strftime("%m/%d/%Y")

    prompt = f"""
You are a professional career assistant.

Generate a modern professional cover letter.

STRICT RULES:
- Use today's date: {today_date}
- Start with:

Aakash Kathirvel
aakashkathirvel80@gmail.com | +1 (804) 866 2848

{today_date}

Dear Hiring Manager,

- DO NOT include:
Hiring Manager
Company Team
Company Address

- Keep formatting clean and professional.
- Use concise paragraphs.
- Tailor it to the job description.
- Mention relevant AI/ML, computer vision, data science, and software engineering skills from the resume.
- End with:

Sincerely,
Aakash Kathirvel

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
