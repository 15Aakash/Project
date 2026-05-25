import requests
import pandas as pd


def search_remoteok_jobs(keyword):

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    blocked_words = [
        "teacher",
        "teaching",
        "tutor",
        "education",
        "curriculum",
        "profesor",
        "profesores",
        "instructor",
        "training",
        "support",
        "help desk",
        "customer support",
        "sales",
        "marketing",
        "admin",
        "data entry",
        "non tech",
        "non-tech"
    ]

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

        search_words = [
            word.strip().lower()
            for word in keyword.split()
            if word.strip() != ""
        ]

        if len(search_words) == 0:
            return pd.DataFrame()

        for job in data[1:]:

            title = str(job.get("position", "")).strip()
            company = str(job.get("company", "")).strip()
            location = str(job.get("location", "Remote")).strip()
            tags_list = job.get("tags", [])

            if not isinstance(tags_list, list):
                tags_list = []

            tags = ", ".join(tags_list)
            apply_url = str(job.get("url", "")).strip()

            if title == "":
                continue

            full_text = f"{title} {tags}".lower()

            if any(blocked in full_text for blocked in blocked_words):
                continue

            match_count = sum(
                1 for word in search_words
                if word in full_text
            )

            if match_count >= max(1, len(search_words) // 2):

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
