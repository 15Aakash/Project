import os
import pandas as pd
from datetime import datetime


def get_file_name(username):

    safe_username = username.replace(" ", "_").lower()

    return f"applications_{safe_username}.csv"


def load_applications(username):

    file_name = get_file_name(username)

    if os.path.exists(file_name):

        return pd.read_csv(file_name)

    columns = [
        "date",
        "company",
        "role",
        "job_link",
        "status",
        "notes",
        "interview_date"
    ]

    return pd.DataFrame(columns=columns)


def save_application(
    username,
    company,
    role,
    job_link,
    status,
    notes
):

    applications = load_applications(username)

    duplicate = applications[
        (applications["company"] == company)
        & (applications["role"] == role)
    ]

    if not duplicate.empty:
        return False

    new_application = pd.DataFrame(
        [
            {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "company": company,
                "role": role,
                "job_link": job_link,
                "status": status,
                "notes": notes,
                "interview_date": ""
            }
        ]
    )

    applications = pd.concat(
        [applications, new_application],
        ignore_index=True
    )

    file_name = get_file_name(username)

    applications.to_csv(
        file_name,
        index=False
    )

    return True


def delete_application(
    username,
    index
):

    applications = load_applications(username)

    applications = applications.drop(index)

    applications = applications.reset_index(drop=True)

    file_name = get_file_name(username)

    applications.to_csv(
        file_name,
        index=False
    )


def update_application_status(
    username,
    index,
    new_status
):

    applications = load_applications(username)

    applications.loc[index, "status"] = new_status

    file_name = get_file_name(username)

    applications.to_csv(
        file_name,
        index=False
    )


def update_interview_date(
    username,
    index,
    interview_date
):

    applications = load_applications(username)

    applications.loc[index, "interview_date"] = interview_date

    file_name = get_file_name(username)

    applications.to_csv(
        file_name,
        index=False
    )
