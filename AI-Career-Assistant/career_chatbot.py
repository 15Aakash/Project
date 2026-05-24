import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def career_chatbot_response(resume_text, chat_history, user_question):

    history_text = ""

    for chat in chat_history:
        history_text += f"User: {chat['question']}\n"
        history_text += f"Assistant: {chat['answer']}\n\n"

    prompt = f"""
You are an AI Career Coach.

Use the resume and previous conversation to answer the user's question.

Rules:
- Be practical
- Give clear steps
- Do not exaggerate
- Keep the answer career-focused
- Explain in simple language
- Use previous conversation context when useful

Resume:
{resume_text}

Previous Conversation:
{history_text}

Current User Question:
{user_question}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0
    )

    return response.output_text
