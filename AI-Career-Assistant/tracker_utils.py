import pandas as pd
import os

CSV_FILE = "applications.csv"


def initialize_tracker():

    if not os.path.exists(CSV_FILE):

        df = pd.DataFrame(
            columns=[
                "date",
                "company",
                "role",
                "job_link",
                "status",
                "notes"
            ]
        )

        df.to_csv(CSV_FILE, index=False)


def load_applications():

    initialize_tracker()

    return pd.read_csv(CSV_FILE)


def save_application(
    company,
    role,
    job_link,
    status,
    notes
):

    initialize_tracker()

    df = pd.read_csv(CSV_FILE)

    duplicate = df[
        (df["company"] == company) &
        (df["role"] == role)
    ]

    if not duplicate.empty:
        return False

    new_row = {
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "company": company,
        "role": role,
        "job_link": job_link,
        "status": status,
        "notes": notes
    }

    df = pd.concat(
        [df, pd.DataFrame([new_row])],
        ignore_index=True
    )

    df.to_csv(CSV_FILE, index=False)

    return True


def delete_application(index):

    df = pd.read_csv(CSV_FILE)

    df = df.drop(index)

    df.to_csv(CSV_FILE, index=False)
