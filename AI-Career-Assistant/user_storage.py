import os
import json


def get_safe_username(username):

    return username.replace(" ", "_").lower()


def get_resume_file(username):

    safe_username = get_safe_username(username)

    return f"saved_resume_{safe_username}.json"


def save_resume_text(username, resume_text):

    file_name = get_resume_file(username)

    data = {
        "resume_text": resume_text
    }

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_resume_text(username):

    file_name = get_resume_file(username)

    if not os.path.exists(file_name):
        return ""

    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("resume_text", "")
