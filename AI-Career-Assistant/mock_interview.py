import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def interviewer_chat(
    resume_text,
    job_description,
    conversation_history
):

    history_text = ""

   for item in conversation_history:

    if "interviewer" not in item:
        continue

        history_text += f"""
Interviewer: {item['interviewer']}
Candidate: {item['candidate']}
"""

    prompt = f"""
You are a professional AI interviewer.

Conduct a realistic interview conversation.

Rules:
- Ask ONE question at a time.
- Respond naturally like a human interviewer.
- Sometimes ask follow-up questions.
- Mix technical, behavioral, and resume-based questions.
- Keep the interview conversational.
- Do not provide answers.
- Do not repeat previous questions.
- Keep responses concise and realistic.

Resume:
{resume_text}

Job Description:
{job_description}

Conversation History:
{history_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.7
    )

    return response.output_text


def evaluate_interview_answer(
    interviewer_question,
    candidate_answer,
    resume_text,
    job_description
):

    prompt = f"""
You are an expert AI interview evaluator.

Evaluate the candidate's interview answer.

Return:
1. Score out of 10
2. Strengths
3. Weaknesses
4. Improved Answer
5. Interview Tips

Question:
{interviewer_question}

Candidate Answer:
{candidate_answer}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return response.output_text
