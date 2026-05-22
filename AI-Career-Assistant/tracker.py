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
    }])

    if os.path.exists(FILE_NAME):
        old_data = pd.read_csv(FILE_NAME)
        data = pd.concat([old_data, new_data], ignore_index=True)
    else:
        data = new_data

    data.to_csv(FILE_NAME, index=False)


def load_applications():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame()