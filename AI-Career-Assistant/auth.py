import json
import hashlib
import os

USER_FILE = "users.json"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    with open(USER_FILE, "r") as file:
        return json.load(file)


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def signup_user(username, password):
    users = load_users()

    if username in users:
        return False

    users[username] = {
        "password": hash_password(password)
    }

    save_users(users)
    return True


def login_user(username, password):
    users = load_users()

    if username not in users:
        return False

    return users[username]["password"] == hash_password(password)
