import pandas as pd
import os

FILE_NAME = "applications.csv"


def load_applications():

    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)

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
    company,
    role,
    job_link,
    status,
    notes
):

    data = load_applications()

    duplicate = data[
        (data["company"] == company)
        &
        (data["role"] == role)
    ]

    if not duplicate.empty:
        return False

    new_row = {
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "company": company,
        "role": role,
        "job_link": job_link,
        "status": status,
        "notes": notes,
        "interview_date": ""
    }

    data = pd.concat(
        [data, pd.DataFrame([new_row])],
        ignore_index=True
    )

    data.to_csv(FILE_NAME, index=False)

    return True


def delete_application(index):

    data = load_applications()

    data = data.drop(index)

    data.to_csv(FILE_NAME, index=False)


def update_application_status(index, new_status):

    data = load_applications()

    data.loc[index, "status"] = new_status

    data.to_csv(FILE_NAME, index=False)


def update_interview_date(index, interview_date):

    data = load_applications()

    data.loc[index, "interview_date"] = interview_date

    data.to_csv(FILE_NAME, index=False)
