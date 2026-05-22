import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def analyze_job_match(resume_text, job_description):

    prompt = f"""
You are an ATS resume analyzer.

Analyze the resume against the job description.

Return ONLY valid JSON.

Format:

{{
    "match_score": "",
    "strong_skills": [],
    "missing_skills": [],
    "keywords_to_add": [],
    "resume_improvements": [],
    "final_decision": "",
    "reason": ""
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    result = response.output_text

    return json.loads(result)