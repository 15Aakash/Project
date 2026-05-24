import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_mock_question(resume_text, job_description, chat_history):

    history_text = ""

    for chat in chat_history:
        history_text += f"Question: {chat['question']}\n"
        history_text += f"Answer: {chat['answer']}\n"
        history_text += f"Feedback: {chat['feedback']}\n\n"

    prompt = f"""
You are an AI mock interview coach.

Based on the resume, job description, and previous interview history,
ask ONE realistic interview question.

Rules:
- Ask only one question.
- Do not provide the answer.
- Mix technical, behavioral, and resume-based questions.
- Do not repeat previous questions.
- Keep it concise.

Resume:
{resume_text}

Job Description:
{job_description}

Previous Interview History:
{history_text}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return response.output_text


def evaluate_mock_answer(question, user_answer, resume_text, job_description):

    prompt = f"""
You are an AI interview evaluator.

Evaluate the user's answer to the interview question.

Return:

Score: /10

Feedback:
[short feedback]

Improved Answer:
[better version of the answer]

Question:
{question}

User Answer:
{user_answer}

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
