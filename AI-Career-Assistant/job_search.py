import requests
import pandas as pd


def search_remoteok_jobs(keyword):

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        if response.status_code != 200:
            return pd.DataFrame()

        data = response.json()

        jobs = []

        search_words = keyword.lower().split()

        for job in data[1:]:

            title = str(job.get("position", ""))
            company = str(job.get("company", ""))
            location = str(job.get("location", "Remote"))
            tags_list = job.get("tags", [])

            if not isinstance(tags_list, list):
                tags_list = []

            tags = ", ".join(tags_list)
            apply_url = str(job.get("url", ""))

            full_text = f"{title} {company} {location} {tags}".lower()

            if any(word in full_text for word in search_words):

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

    except Exception:

        return pd.DataFrame()
