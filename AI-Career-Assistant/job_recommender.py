import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def recommend_jobs(resume_text):

    prompt = f"""
You are an AI career advisor.

Based on the resume, recommend the best job roles.

Return ONLY valid JSON.

Format:
{{
    "recommended_roles": [
        {{
            "role": "",
            "match_score": "",
            "why_good_fit": "",
            "missing_skills": [],
            "learning_plan": []
        }}
    ]
}}

Recommend 5 roles.

Resume:
{resume_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return json.loads(response.output_text)