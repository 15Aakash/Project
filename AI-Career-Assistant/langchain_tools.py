from langchain_core.tools import tool


@tool
def ats_tool(user_input: str) -> str:
    """Use this tool when the user wants ATS analysis or job match scoring."""
    return "ATS_AGENT"


@tool
def resume_tailor_tool(user_input: str) -> str:
    """Use this tool when the user wants resume tailoring or resume improvement."""
    return "RESUME_TAILOR_AGENT"


@tool
def cover_letter_tool(user_input: str) -> str:
    """Use this tool when the user wants a cover letter."""
    return "COVER_LETTER_AGENT"


@tool
def recruiter_tool(user_input: str) -> str:
    """Use this tool when the user wants recruiter outreach or LinkedIn message."""
    return "RECRUITER_AGENT"


@tool
def interview_tool(user_input: str) -> str:
    """Use this tool when the user wants interview preparation questions."""
    return "INTERVIEW_COACH_AGENT"


@tool
def mock_interview_tool(user_input: str) -> str:
    """Use this tool when the user wants a live mock interview."""
    return "MOCK_INTERVIEW_AGENT"


@tool
def career_coach_tool(user_input: str) -> str:
    """Use this tool when the user wants career advice or learning roadmap."""
    return "CAREER_COACH_AGENT"


@tool
def tracker_tool(user_input: str) -> str:
    """Use this tool when the user wants to track or manage applications."""
    return "TRACKER_AGENT"


career_tools = [
    ats_tool,
    resume_tailor_tool,
    cover_letter_tool,
    recruiter_tool,
    interview_tool,
    mock_interview_tool,
    career_coach_tool,
    tracker_tool
]
