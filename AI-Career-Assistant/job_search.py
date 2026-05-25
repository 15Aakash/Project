import requests
import pandas as pd


def search_remoteok_jobs(keyword):

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()

    jobs = []

    for job in data[1:]:

        title = job.get("position", "")
        company = job.get("company", "")
        location = job.get("location", "Remote")
        tags = ", ".join(job.get("tags", []))
        apply_url = job.get("url", "")

        text = f"{title} {company} {tags}".lower()

        if keyword.lower() in text:

            jobs.append(
                {
                    "company": company,
                    "role": title,
                    "location": location,
                    "skills": tags,
                    "job_link": apply_url,
                    "source": "RemoteOK"
                }
            )

    return pd.DataFrame(jobs)
