def execute_selected_agent(
    selected_agent,
    user_request,
    resume_text,
    job_description,
    interview_agent,
    recruiter_agent,
    cover_letter_agent,
    resume_tailor_agent,
    career_coach_agent,
    coach_history
):

    if selected_agent == "INTERVIEW_COACH_AGENT":

        return interview_agent.generate(
            resume_text,
            user_request
        )

    elif selected_agent == "RECRUITER_AGENT":

        return recruiter_agent.generate(
            resume_text,
            user_request
        )

    elif selected_agent == "COVER_LETTER_AGENT":

        return cover_letter_agent.generate(
            resume_text,
            user_request
        )

    elif selected_agent == "RESUME_TAILOR_AGENT":

        return resume_tailor_agent.generate(
            resume_text,
            job_description
        )

    elif selected_agent == "CAREER_COACH_AGENT":

        return career_coach_agent.chat(
            resume_text,
            coach_history,
            user_request
        )

    elif selected_agent == "ATS_AGENT":

        return "ATS Agent selected. Please use the Match Dashboard or Autonomous Workflow to run full ATS analysis."

    elif selected_agent == "MOCK_INTERVIEW_AGENT":

        return "Mock Interview Agent selected. Please open Mock Interview to start a live interview session."

    elif selected_agent == "TRACKER_AGENT":

        return "Tracker Agent selected. Please open Tracker to manage applications."

    else:

        return "I could not identify the correct agent."
