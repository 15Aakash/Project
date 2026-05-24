import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_interview_questions(resume_text, job_description):

    prompt = f"""
You are an expert AI/ML interview coach.

Create a clean, professional interview preparation document.

Important rules:
- Do NOT start with "Certainly".
- Do NOT end with "If you want".
- Do NOT use markdown symbols like ###, **, or ---.
- Use clean plain headings.
- Make the text professional and readable.
- Do not exaggerate the candidate's experience.
- If the job requires something the candidate lacks, say how to answer honestly.
- Focus on AI/ML, computer vision, Python, research, projects, and communication.
- Include 5 technical questions, 5 behavioral questions, 5 resume-based questions.
- Include short sample answers under each question.
- Keep answers realistic for a fresher/early-career candidate.

Use this format exactly:

INTERVIEW PREPARATION GUIDE

1. TECHNICAL INTERVIEW QUESTIONS

Question 1:
Answer:

Question 2:
Answer:

2. BEHAVIORAL INTERVIEW QUESTIONS

Question 1:
Answer:

3. RESUME-BASED QUESTIONS

Question 1:
Answer:

4. SKILL GAPS TO PREPARE

5. FINAL INTERVIEW STRATEGY

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
