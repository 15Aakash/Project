from langchain_tools import (
    ats_tool,
    resume_tailor_tool,
    cover_letter_tool,
    recruiter_tool,
    interview_tool,
    mock_interview_tool,
    career_coach_tool,
    tracker_tool
)


def run_langchain_tool_agent(user_request):

    request = user_request.lower()

    if "cover letter" in request:
        return cover_letter_tool.invoke(user_request)

    if "resume" in request or "tailor" in request:
        return resume_tailor_tool.invoke(user_request)

    if "recruiter" in request or "linkedin" in request or "outreach" in request:
        return recruiter_tool.invoke(user_request)

    if "mock interview" in request:
        return mock_interview_tool.invoke(user_request)

    if "interview" in request:
        return interview_tool.invoke(user_request)

    if "track" in request or "application" in request:
        return tracker_tool.invoke(user_request)

    if "career" in request or "roadmap" in request:
        return career_coach_tool.invoke(user_request)

    if "ats" in request or "match" in request:
        return ats_tool.invoke(user_request)

    return career_coach_tool.invoke(user_request)
