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

Based on the resume and job description, create copy-paste ready resume replacement sections.

IMPORTANT RULES:
- Do not invent fake experience.
- Use only skills, projects, and experience already present in the resume.
- Make it ATS-friendly.
- Make bullets concise and professional.
- Use strong action verbs.
- Include measurable impact only if supported by the resume.
- Clearly tell the user which section to replace.

Return in this exact format:

SECTION 1: PROFESSIONAL SUMMARY
Replace your current summary with:
[write improved summary here]

SECTION 2: SKILLS
Replace or update your skills section with:
[write improved skills here]

SECTION 3: EXPERIENCE BULLETS
Replace or add these bullets under relevant experience:
- bullet 1
- bullet 2
- bullet 3
- bullet 4

SECTION 4: PROJECT BULLETS
Replace or add these bullets under relevant projects:
- bullet 1
- bullet 2
- bullet 3
- bullet 4

SECTION 5: ATS KEYWORDS TO INCLUDE
Add these naturally if true:
- keyword 1
- keyword 2
- keyword 3

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
