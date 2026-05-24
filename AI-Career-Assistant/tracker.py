import pandas as pd
from datetime import date
import os

FILE_NAME = "applications.csv"


def save_application(company, role, job_link, status, notes):

    new_data = pd.DataFrame([{
        "date": date.today(),
        "company": company,
        "role": role,
        "job_link": job_link,
        "status": status,
        "notes": notes
        "interview_date": ""
    }])

    if os.path.exists(FILE_NAME):

        data = pd.read_csv(FILE_NAME)

        duplicate = data[
            (data["company"].str.lower() == company.lower()) &
            (data["role"].str.lower() == role.lower()) &
            (data["job_link"].str.lower() == job_link.lower())
        ]

        if not duplicate.empty:
            return False

        data = pd.concat([data, new_data], ignore_index=True)

    else:
        data = new_data

    data.to_csv(FILE_NAME, index=False)

    return True


def load_applications():

    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)

    return pd.DataFrame()


def delete_application(index):

    if os.path.exists(FILE_NAME):

        data = pd.read_csv(FILE_NAME)

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
