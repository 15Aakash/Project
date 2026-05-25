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

        interviewer_q = item.get("interviewer", "")
        candidate_a = item.get("candidate", "")

        if interviewer_q.strip() == "" and candidate_a.strip() == "":
            continue

        history_text += f"""
Previous Interview Question:
{interviewer_q}

Candidate Answer:
{candidate_a}
"""

    prompt = f"""
You are a professional senior AI/ML interviewer conducting a realistic live interview.

Your rules:
- Act like a real interviewer.
- Ask only ONE question at a time.
- Do not repeat previous questions.
- Use the candidate's previous answers to ask intelligent follow-up questions.
- If the candidate gives a strong answer, go deeper technically.
- If the candidate gives a weak answer, ask a helpful follow-up.
- Mix technical, behavioral, resume-based, and problem-solving questions.
- Do not provide answers or hints.
- Keep it conversational and concise.
- Avoid repeating the same introduction every time.

Resume:
{resume_text}

Job Description:
{job_description}

Interview History:
{history_text}

Continue the interview naturally with the next best question only.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.8
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

Return in this clean format:

Score: /10

Strengths:
-

Weaknesses:
-

Improved Answer:
[write a stronger interview answer]

Interview Tips:
-

Rules:
- Be honest but encouraging.
- Do not use markdown symbols like #, ##, **, or ---.
- Keep feedback practical and interview-focused.

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

def transcribe_audio(audio_file_path):

    with open(audio_file_path, "rb") as audio_file:

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return transcript.text

def generate_ai_voice(
    text,
    output_path
):

    speech = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )

    speech.stream_to_file(output_path)

    return output_path
