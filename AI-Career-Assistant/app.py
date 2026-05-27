import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


from agents import (
    ResumeAgent,
    ATSAgent,
    RecommendationAgent,
    CoverLetterAgent,
    RecruiterAgent,
    ResumeTailorAgent,
    InterviewCoachAgent,
    CareerCoachAgent,
    MockInterviewAgent
)

from tracker import (
    save_application,
    load_applications,
    delete_application,
    update_application_status,
    update_interview_date
)

from pdf_generator import create_pdf
from streamlit_mic_recorder import mic_recorder
from auth import signup_user, login_user
from agent_router import route_user_request
from langchain_agent import langchain_route_request
from langchain_executor import run_langchain_tool_agent
from agent_executor_tools import execute_selected_agent
from rag_memory import save_memory, search_memory, retrieve_memory_context
from datetime import datetime
from zoneinfo import ZoneInfo

from user_storage import (
    save_resume_text,
    load_resume_text,
    save_ats_report,
    load_ats_reports,
    save_mock_interview,
    load_mock_interviews
)


st.set_page_config(
    page_title="AI Career Assistant",
    layout="wide",
    page_icon="🤖"
)

# -----------------------------
# LOGIN / SIGNUP PAGE
# -----------------------------

if not st.session_state.get("logged_in", False):

    st.title("🧠 Welcome to AI Career Assistant")

    st.markdown(
        "Your AI-powered career copilot for resume optimization, ATS matching, "
        "interview preparation, and recruiter outreach."
    )

    st.markdown("---")

    st.subheader("🔐 Login or Create Account")

    auth_mode = st.radio(
        "Choose Option",
        ["Login", "Sign Up"],
        horizontal=True
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Sign Up":

        if st.button("Create Account", use_container_width=True):

            if username.strip() == "" or password.strip() == "":
                st.warning("Please enter username and password.")

            else:
                created = signup_user(username.strip(), password)

                if created:
                    st.success("Account created successfully. Please login.")
                else:
                    st.warning("Username already exists.")

    else:

        if st.button("🚀 Continue to Dashboard", use_container_width=True):

            if username.strip() == "" or password.strip() == "":
                st.warning("Please enter username and password.")

            elif login_user(username.strip(), password):

                # Save login details
                st.session_state.logged_in = True
                st.session_state.username = username.strip()

                # Clear old generated content immediately after login
                old_keys_to_clear = [
                    "resume_text",
                    "job_description",
                    "cover_letter",
                    "resume_tailor_result",
                    "recruiter_message",
                    "interview_questions",
                    "career_coach_response",
                    "ai_assistant_chat",
                    "coach_history",
                    "match_result",
                    "job_recommendations",
                    "mock_interview_result",
                    "tracker_data",
                    "selected_job",
                    "uploaded_resume",
                    "uploaded_job_description"
                ]

                for key in old_keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

                st.success("Login successful.")
                st.rerun()

            else:
                st.error("Invalid username or password.")

    st.stop()


# -----------------------------
# USER-SPECIFIC SESSION SETUP
# -----------------------------

current_user = st.session_state.username

# Create user-specific keys
resume_text_key = f"resume_text_{current_user}"
job_description_key = f"job_description_{current_user}"
cover_letter_key = f"cover_letter_{current_user}"
resume_tailor_key = f"resume_tailor_result_{current_user}"
recruiter_key = f"recruiter_message_{current_user}"
interview_key = f"interview_questions_{current_user}"
career_key = f"career_coach_response_{current_user}"
chat_key = f"ai_assistant_chat_{current_user}"
coach_history_key = f"coach_history_{current_user}"
match_result_key = f"match_result_{current_user}"
job_recommendations_key = f"job_recommendations_{current_user}"
mock_interview_key = f"mock_interview_result_{current_user}"
tracker_key = f"tracker_data_{current_user}"

# Initialize user-specific values
if resume_text_key not in st.session_state:
    st.session_state[resume_text_key] = ""

if job_description_key not in st.session_state:
    st.session_state[job_description_key] = ""

if cover_letter_key not in st.session_state:
    st.session_state[cover_letter_key] = ""

if resume_tailor_key not in st.session_state:
    st.session_state[resume_tailor_key] = ""

if recruiter_key not in st.session_state:
    st.session_state[recruiter_key] = ""

if interview_key not in st.session_state:
    st.session_state[interview_key] = ""

if career_key not in st.session_state:
    st.session_state[career_key] = ""

if chat_key not in st.session_state:
    st.session_state[chat_key] = []

if coach_history_key not in st.session_state:
    st.session_state[coach_history_key] = []

if match_result_key not in st.session_state:
    st.session_state[match_result_key] = ""

if job_recommendations_key not in st.session_state:
    st.session_state[job_recommendations_key] = ""

if mock_interview_key not in st.session_state:
    st.session_state[mock_interview_key] = ""

if tracker_key not in st.session_state:
    st.session_state[tracker_key] = []


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🧠 AI Career Assistant")

st.sidebar.caption(f"Logged in as: {st.session_state.username}")

st.sidebar.divider()

st.sidebar.markdown("### 🚀 AI Features")

st.sidebar.markdown("""
- Resume Analysis
- ATS Optimization
- AI Interview Prep
- Recruiter Outreach
- Career Coaching
- Application Tracking
""")

st.sidebar.divider()


# -----------------------------
# LOGOUT
# -----------------------------

if st.sidebar.button("Logout"):

    # Clear everything from current browser session
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


st.markdown("""

<h1 style='font-size:48px;'>
🤖 AI Career Assistant
</h1>
""", unsafe_allow_html=True)

st.write(
    "A multi-agent AI career platform for resume matching, ATS optimization, job recommendations, interview preparation, and application tracking."
)

st.markdown("---")

resume_agent = ResumeAgent()
ats_agent = ATSAgent()
recommendation_agent = RecommendationAgent()
cover_letter_agent = CoverLetterAgent()
recruiter_agent = RecruiterAgent()
resume_tailor_agent = ResumeTailorAgent()
interview_agent = InterviewCoachAgent()
career_coach_agent = CareerCoachAgent()
mock_interview_agent = MockInterviewAgent()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "mock_history" not in st.session_state:
    st.session_state.mock_history = []

if "current_mock_question" not in st.session_state:
    st.session_state.current_mock_question = ""

if "mock_chat" not in st.session_state:
    st.session_state.mock_chat = []

if "mock_feedback" not in st.session_state:
    st.session_state.mock_feedback = []

if "resume_loaded" not in st.session_state:
    st.session_state.resume_loaded = False

if not st.session_state.resume_loaded:
    saved_resume = load_resume_text(st.session_state.username)

    if saved_resume:
        st.session_state.resume_text = saved_resume

    st.session_state.resume_loaded = True

if "mock_started" not in st.session_state:
    st.session_state.mock_started = False

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "coach_history" not in st.session_state:
    st.session_state.coach_history = []

if "recommendations" not in st.session_state:
    st.session_state.recommendations = None

if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""

if "recruiter_message" not in st.session_state:
    st.session_state.recruiter_message = ""

if "tailored_resume" not in st.session_state:
    st.session_state.tailored_resume = ""

if "interview_questions" not in st.session_state:
    st.session_state.interview_questions = ""

if "mock_scores" not in st.session_state:
    st.session_state.mock_scores = ""

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "📊 Match Dashboard"

if "auto_workflow_result" not in st.session_state:
    st.session_state.auto_workflow_result = None

if "ai_assistant_chat" not in st.session_state:
    st.session_state.ai_assistant_chat = []

col1, col2 = st.columns([1, 2])

with col1:
    resume_file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx"]
    )

with col2:
    job_description = st.text_area(
        "Paste Job Description",
        height=180
    )

if st.button("🚀 Analyze Job"):

    if resume_file is None:
        st.warning("Please upload your resume first.")

    elif job_description.strip() == "":
        st.warning("Please paste the job description.")

    else:
        with st.spinner("Resume Agent is reading your resume..."):
            st.session_state.resume_text = resume_agent.parse_resume(
                resume_file
            )
            
            save_memory(
                st.session_state.username,
                st.session_state.resume_text,
                {
                    "type": "resume"
                }
            )
            
            save_resume_text(
                st.session_state.username,
                st.session_state.resume_text
            )    

        with st.spinner("ATS Agent is analyzing job match..."):
            st.session_state.analysis = ats_agent.analyze(
                st.session_state.resume_text,
                job_description
            )

            save_ats_report(
                st.session_state.username,
                job_description,
                st.session_state.analysis
            )

        st.success("Multi-agent analysis completed successfully!")

st.markdown("---")
def map_agent_to_page(agent_name):

    mapping = {
        "ATS_AGENT": "📊 Match Dashboard",
        "RESUME_TAILOR_AGENT": "📝 Resume Tailor",
        "COVER_LETTER_AGENT": "✍️ Cover Letter",
        "RECRUITER_AGENT": "💬 Recruiter Outreach",
        "INTERVIEW_COACH_AGENT": "🎤 Interview Coach",
        "MOCK_INTERVIEW_AGENT": "🎙️ Mock Interview",
        "CAREER_COACH_AGENT": "💬 AI Career Coach",
        "TRACKER_AGENT": "📌 Tracker"
    }

    return mapping.get(agent_name, "📊 Match Dashboard")
    
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "🧠 AI Assistant"

        
page = st.session_state.selected_page
    
# Conversational AI Assistant

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

st.markdown("<br>", unsafe_allow_html=True)

st.header("🧠 Conversational AI Assistant")

st.caption(
    "Your intelligent AI career copilot for resume optimization, interview preparation, "
    "recruiter outreach, and job application workflows."
)

# Initialize chat history
if "ai_assistant_chat" not in st.session_state:
    st.session_state.ai_assistant_chat = []

# Clear chat button
if st.button("🧹 Clear Chat"):
    st.session_state.ai_assistant_chat = []
    st.rerun()

# Display previous chat history
for chat in st.session_state.ai_assistant_chat:
    with st.chat_message("user"):
        st.markdown(chat["user"])

    with st.chat_message("assistant"):
        st.markdown(chat["assistant"])

# Chat input
user_request = st.chat_input("Ask your AI Career Assistant...")

if user_request:

    with st.chat_message("user"):
        st.markdown(user_request)

    with st.spinner("AI Assistant is thinking..."):

        selected_agent = run_langchain_tool_agent(user_request)

        memory_context = retrieve_memory_context(
            st.session_state.username,
            user_request
        )

        if selected_agent == "INTERVIEW_COACH_AGENT":

            enhanced_prompt = f"""
User Request:
{user_request}

Job Description:
{job_description}

Relevant Resume Memory:
{memory_context}
"""

            agent_response = interview_agent.generate(
                st.session_state.resume_text,
                enhanced_prompt
            )

            response = f"""
**Interview Coach Agent**

Here are interview questions:

{agent_response}
"""

        elif selected_agent == "RECRUITER_AGENT":

            enhanced_prompt = f"""
User Request:
{user_request}

Job Description:
{job_description}

Relevant Resume Memory:
{memory_context}
"""

            agent_response = recruiter_agent.generate(
                st.session_state.resume_text,
                enhanced_prompt
            )

            response = f"""
**Recruiter Outreach Agent**

Generated recruiter message:

{agent_response}
"""

        elif selected_agent == "COVER_LETTER_AGENT":

            today_date = datetime.now(
                ZoneInfo("America/New_York")
            ).strftime("%m/%d/%Y")

            enhanced_prompt = f"""
User Request:
{user_request}

Job Description:
{job_description}

Relevant Resume Memory:
{memory_context}

Important Rules:
- Generate ONLY the cover letter body.
- Do NOT include my name.
- Do NOT include my email.
- Do NOT include my phone number.
- Do NOT include any date.
- Do NOT include "Dear Hiring Manager,".
- Do NOT include "Sincerely," or my name at the end.
- Start directly with the first paragraph.
- Use the company name ONLY if it is explicitly mentioned in the job description.
- If no company name is found, write "your organization" instead.
- Do NOT guess company names.
- Do NOT reuse company names from previous chats or memory.
- Generate a professional ATS-friendly cover letter.
"""

            agent_response = cover_letter_agent.generate(
                st.session_state.resume_text,
                enhanced_prompt
            )

            response = f"""
**Cover Letter Agent**

Generated cover letter:

Aakash Kathirvel  
aakashkathirvel80@gmail.com | +1 (804) 866 2848  

{today_date}  

Dear Hiring Manager,  

{agent_response}

Sincerely,  
Aakash Kathirvel
"""

        elif selected_agent == "RESUME_TAILOR_AGENT":

            enhanced_prompt = f"""
User Request:
{user_request}

Job Description:
{job_description}

Relevant Resume Memory:
{memory_context}
"""

            agent_response = resume_tailor_agent.generate(
                st.session_state.resume_text,
                enhanced_prompt
            )

            response = f"""
**Resume Tailor Agent**

{agent_response}
"""

        elif selected_agent == "CAREER_COACH_AGENT":

            enhanced_request = f"""
User Question:
{user_request}

Job Description:
{job_description}

Relevant Memory:
{memory_context}
"""

            agent_response = career_coach_agent.chat(
                st.session_state.resume_text,
                st.session_state.coach_history,
                enhanced_request
            )

            response = f"""
**Career Coach Agent**

{agent_response}
"""

        else:

            response = f"""
**AI Assistant**

I routed your request to: **{selected_agent}**

Please open the matching tool below if needed.
"""

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.ai_assistant_chat.append(
        {
            "user": user_request,
            "assistant": response
        }
    )

    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
st.divider()
st.markdown("### Advanced Tools")
pages = [
    "📊 Match Dashboard",
    "🎯 Job Recommendations",
    "✍️ Cover Letter",
    "💬 Recruiter Outreach",
    "📄 Resume Tailor",
    "🎤 Interview Coach",
    "🧠 AI Career Coach",
    "🎙️ Mock Interview",
    "📌 Tracker"
]

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "📊 Match Dashboard"

page = st.radio(
    "",
    pages,
    index=pages.index(st.session_state.selected_page),
    horizontal=True,
    key="navigation_radio"
)

st.session_state.selected_page = page

if page == "📊 Match Dashboard":

    st.header("📊 AI Job Match Dashboard")

    if st.session_state.analysis is None:
        st.info("Upload your resume,paste a job description,and click Analyze Job.")

    else:
        analysis = st.session_state.analysis

        score_text = str(
            analysis["match_score"]
        ).replace("%", "").replace("/100", "").strip()

        try:
            score = int(score_text)
        except:
            score = 0

        if score >= 75:
            readiness = "High"
        elif score >= 50:
            readiness = "Medium"
        else:
            readiness = "Low"

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Match Score", f"{score}%")

        with col2:
            st.write("### Decision")
            st.info(analysis["final_decision"])

        with col3:
            st.metric("Missing Skills", len(analysis["missing_skills"]))

        with col4:
            st.metric("ATS Readiness", readiness)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "ATS Match Score"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "royalblue"},
                "steps": [
                    {"range": [0, 50], "color": "#ffcccc"},
                    {"range": [50, 75], "color": "#fff2cc"},
                    {"range": [75, 100], "color": "#d9ead3"}
                ],
            }
        ))

        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ Strong Matching Skills")
            for skill in analysis["strong_skills"]:
                st.success(skill)

        with col2:
            st.subheader("⚠️ Missing Skills")
            for skill in analysis["missing_skills"]:
                st.error(skill)

        st.subheader("🎯 ATS Keywords To Add")
        for keyword in analysis["keywords_to_add"]:
            st.info(keyword)

        st.subheader("🛠 Resume Improvements")
        for improvement in analysis["resume_improvements"]:
            st.warning(improvement)

        st.subheader("🧠 Reason")
        st.write(analysis["reason"])

        ats_report = f"""
AI Job Match Report

Match Score: {score}%
Decision: {analysis["final_decision"]}
ATS Readiness: {readiness}
Missing Skills Count: {len(analysis["missing_skills"])}

Strong Matching Skills:
{chr(10).join(["- " + skill for skill in analysis["strong_skills"]])}

Missing Skills:
{chr(10).join(["- " + skill for skill in analysis["missing_skills"]])}

ATS Keywords To Add:
{chr(10).join(["- " + keyword for keyword in analysis["keywords_to_add"]])}

Resume Improvements:
{chr(10).join(["- " + improvement for improvement in analysis["resume_improvements"]])}

Reason:
{analysis["reason"]}
"""

        pdf_path = create_pdf(
            "AI Job Match Report",
            ats_report,
            "ats_report.pdf"
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download ATS Report as PDF",
                data=pdf_file,
                file_name="ats_report.pdf",
                mime="application/pdf"
            )

        with st.expander("View Extracted Resume Text"):
            
            st.text_area(
                "Resume Content",
                st.session_state.resume_text,
                height=300
            )


        st.markdown("---")

        st.subheader("📁 Saved ATS Reports")

        saved_reports = load_ats_reports(
            st.session_state.username
        )
        
        if len(saved_reports) == 0:
        
            st.info("No saved ATS reports yet.")
        
        else:
        
            for idx, report in enumerate(
                reversed(saved_reports)
            ):
        
                analysis = report["analysis"]
        
                with st.expander(
                    f"{report['date']} | Match Score: {analysis['match_score']}"
                ):
        
                    st.write("### Job Description")
                    st.write(report["job_description"])
        
                    st.write("### Decision")
                    st.info(
                        analysis["final_decision"]
                    )
        
                    st.write("### Strong Skills")
        
                    for skill in analysis["strong_skills"]:
                        st.success(skill)
        
                    st.write("### Missing Skills")
        
                    for skill in analysis["missing_skills"]:
                        st.warning(skill)
        
                    st.write("### Resume Improvements")
        
                    for improvement in analysis[
                        "resume_improvements"
                    ]:
                        st.write("- " + improvement)
                
elif page == "🎯 Job Recommendations":

    if (
        "resume_text" not in st.session_state
        or st.session_state.resume_text is None
        or st.session_state.resume_text.strip() == ""
    ):
        st.header("🎯 AI Job Recommendation Engine")
        st.info("Analyze a job first to generate Job Recommendations.")
        st.stop()

    st.header("🎯 AI Job Recommendation Engine")

    if st.button("Generate Job Recommendations", use_container_width=True):

        with st.spinner("Recommendation Agent is finding best matching roles..."):
            st.session_state.recommendations = recommendation_agent.recommend(
                st.session_state.resume_text
            )

    if st.session_state.recommendations is not None:

        recommendation_text = ""

        for item in st.session_state.recommendations["recommended_roles"]:

            st.markdown("---")
            st.subheader(item["role"])
            st.metric("Role Match Score", item["match_score"])

            st.write("### Why this is a good fit:")
            st.write(item["why_good_fit"])

            col1, col2 = st.columns(2)

            with col1:
                st.write("### Missing Skills:")
                for skill in item["missing_skills"]:
                    st.warning(skill)

            with col2:
                st.write("### Learning Plan:")
                for step in item["learning_plan"]:
                    st.info(step)

            recommendation_text += f"""
Role: {item["role"]}
Match Score: {item["match_score"]}

Why Good Fit:
{item["why_good_fit"]}

Missing Skills:
{chr(10).join(["- " + skill for skill in item["missing_skills"]])}

Learning Plan:
{chr(10).join(["- " + step for step in item["learning_plan"]])}

----------------------------------------
"""

        pdf_path = create_pdf(
            "AI Job Recommendations",
            recommendation_text,
            "job_recommendations.pdf"
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download Job Recommendations as PDF",
                data=pdf_file,
                file_name="job_recommendations.pdf",
                mime="application/pdf"
            )

elif page == "✍️ Cover Letter":

    st.header("✍️ Tailored Cover Letter")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate a cover letter.")

    else:
        if st.button("Generate Cover Letter", use_container_width=True):

            with st.spinner("Cover Letter Agent is writing your letter..."):

                # Correct current date based on Virginia / Eastern Time
                today_date = datetime.now(
                    ZoneInfo("America/New_York")
                ).strftime("%m/%d/%Y")

                # Ask AI to generate ONLY the body of the cover letter
                cover_letter_prompt = f"""
You are a professional cover letter writing assistant.

Generate a tailored, ATS-friendly cover letter body using the resume and job description below.

Resume:
{st.session_state.resume_text}

Job Description:
{job_description}

Important Rules:
- Generate ONLY the body paragraphs of the cover letter.
- Do NOT include my name.
- Do NOT include my email.
- Do NOT include my phone number.
- Do NOT include any date.
- Do NOT include "Dear Hiring Manager,".
- Do NOT include "Sincerely,".
- Do NOT include my name at the end.
- Start directly with the first paragraph.
- Use the company name ONLY if it is explicitly mentioned in the job description.
- If no company name is found, write "your organization" instead.
- Do NOT guess the company name.
- Do NOT reuse company names from previous chats or memory.
- Keep the tone professional, confident, and natural.
- Make the letter specific to the role.
- Highlight only relevant skills from the resume.
"""

                cover_letter_body = cover_letter_agent.generate(
                    st.session_state.resume_text,
                    cover_letter_prompt
                )

                # Python creates the fixed header, date, greeting, and closing
                st.session_state.cover_letter = f"""Aakash Kathirvel
aakashkathirvel80@gmail.com | +1 (804) 866 2848

{today_date}

Dear Hiring Manager,

{cover_letter_body}

Sincerely,
Aakash Kathirvel
"""

        if st.session_state.cover_letter:

            edited_cover_letter = st.text_area(
                "Edit Cover Letter Before Download",
                value=st.session_state.cover_letter,
                height=350
            )

            # Save edited version back to session state
            st.session_state.cover_letter = edited_cover_letter

            st.download_button(
                label="Download Edited Cover Letter as TXT",
                data=edited_cover_letter,
                file_name="Aakash_Kathirvel_Cover_Letter.txt",
                mime="text/plain"
            )

            pdf_path = create_pdf(
                "",
                edited_cover_letter,
                "Aakash_Kathirvel_Cover_Letter.pdf"
            )

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Edited Cover Letter as PDF",
                    data=pdf_file,
                    file_name="Aakash_Kathirvel_Cover_Letter.pdf",
                    mime="application/pdf"
                )

elif page == "💬 Recruiter Outreach":

    st.header("💬 LinkedIn Recruiter Outreach Message")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate a recruiter outreach message.")

    else:
        if st.button("Generate Recruiter Outreach Message", use_container_width=True):

            with st.spinner("Recruiter Outreach Agent is generating your message..."):
                st.session_state.recruiter_message = recruiter_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

        if st.session_state.recruiter_message:

            edited_recruiter_message = st.text_area(
                "Edit Recruiter Outreach Message Before Download",
                st.session_state.recruiter_message,
                height=250
            )

            st.download_button(
                label="Download Edited Recruiter Outreach as TXT",
                data=edited_recruiter_message,
                file_name="recruiter_outreach_message.txt",
                mime="text/plain"
            )

            pdf_path = create_pdf(
                "LinkedIn Recruiter Outreach Message",
                edited_recruiter_message,
                "recruiter_outreach_message.pdf"
            )

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Edited Recruiter Outreach as PDF",
                    data=pdf_file,
                    file_name="recruiter_outreach_message.pdf",
                    mime="application/pdf"
                )

elif page == "📄 Resume Tailor":

    if (
        "resume_text" not in st.session_state
        or st.session_state.resume_text is None
        or st.session_state.resume_text.strip() == ""
    ):
        st.header("📄 AI Resume Tailor")
        st.info("Upload your resume, paste a job description, and click Analyze Job first.")
        st.stop()

    st.header("📄 AI Resume Tailor")

    if st.button("Generate Resume Improvements", use_container_width=True):

        with st.spinner("Resume Tailor Agent is optimizing your resume..."):

            st.session_state.tailored_resume = resume_tailor_agent.generate(
                st.session_state.resume_text,
                job_description
            )

    if st.session_state.tailored_resume:

        edited_tailored_resume = st.text_area(
            "Edit Resume Improvements Before Download",
            st.session_state.tailored_resume,
            height=450
        )

        st.download_button(
            label="Download Edited Resume Improvements as TXT",
            data=edited_tailored_resume,
            file_name="tailored_resume_improvements.txt",
            mime="text/plain"
        )

        pdf_path = create_pdf(
            "Tailored Resume Improvements",
            edited_tailored_resume,
            "tailored_resume_improvements.pdf"
        )

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download Edited Resume Improvements as PDF",
                data=pdf_file,
                file_name="tailored_resume_improvements.pdf",
                mime="application/pdf"
            )
            
elif page == "🎤 Interview Coach":

    st.header("🎤 AI Interview Coach")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate interview questions.")

    else:
        if st.button("Generate Interview Questions", use_container_width=True):

            with st.spinner("Interview Coach Agent is preparing questions..."):
                st.session_state.interview_questions = interview_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

        if st.session_state.interview_questions:
                st.markdown(st.session_state.interview_questions)
                st.download_button(
                    label="Download Interview Questions as TXT",
                    data=st.session_state.interview_questions,
                    file_name="interview_questions.txt",
                    mime="text/plain"
                )
                pdf_path = create_pdf(
                    "Interview Preparation Questions",
                     st.session_state.interview_questions,
                    "interview_questions.pdf"
                )
    
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="Download Edited Interview Questions as PDF",
                        data=pdf_file,
                        file_name="interview_questions.pdf",
                        mime="application/pdf"
                    )

elif page == "🧠 AI Career Coach":

    st.header("🧠 AI Career Coach")

    if (
        "resume_text" not in st.session_state
        or st.session_state.resume_text is None
        or st.session_state.resume_text.strip() == ""
    ):
        st.info("Upload your resume, paste a job description, and click Analyze Job first.")

    else:
        st.write("Ask career questions based on your resume, skills, and previous conversation.")

        quick_questions = [
            "What jobs suit me based on my resume?",
            "How can I improve my ATS score?",
            "What skills should I learn next?",
            "Am I ready for AI Engineer roles?",
            "How should I prepare for interviews?"
        ]

        user_question = None

        st.subheader("Quick Questions")

        cols = st.columns(2)

        for i, question in enumerate(quick_questions):
            with cols[i % 2]:
                if st.button(question, key=f"quick_{i}", use_container_width=True):
                    user_question = question

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.coach_history = []
            st.success("Chat history cleared.")
            st.rerun()

        typed_question = st.text_input(
            "Ask your career coach",
            placeholder="Example: What skills should I learn next?"
        )

        if typed_question:
            user_question = typed_question

        if user_question:
            with st.spinner("Career Coach Agent is thinking..."):
                coach_answer = career_coach_agent.chat(
                    st.session_state.resume_text,
                    st.session_state.coach_history,
                    user_question
                )

            st.session_state.coach_history.append(
                {
                    "question": user_question,
                    "answer": coach_answer
                }
            )

        if st.session_state.coach_history:
            st.markdown("---")

            for chat in st.session_state.coach_history:
                with st.chat_message("user"):
                    st.write(chat["question"])

                with st.chat_message("assistant"):
                    st.write(chat["answer"])

elif page == "🎙️ Mock Interview":

    st.header("🎙️ AI Mock Interview")

    interview_mode = st.radio(
        "Choose Interview Mode",
        ["Text Interview", "Voice Interview"],
        horizontal=True
    )

    if (
        st.session_state.resume_text == ""
        or job_description.strip() == ""
    ):
        st.info("Analyze a job first to start the mock interview.")

    else:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Start Interview", use_container_width=True):

                st.session_state.mock_chat = []
                st.session_state.mock_feedback = []
                st.session_state.mock_scores = ""
                st.session_state.mock_started = True

                first_question = mock_interview_agent.interviewer_chat(
                    st.session_state.resume_text,
                    job_description,
                    st.session_state.mock_chat
                )

                st.session_state.mock_chat.append(
                    {
                        "role": "assistant",
                        "content": first_question
                    }
                )

                st.rerun()

        with col2:
            if st.button("Reset Interview", use_container_width=True):

                st.session_state.mock_chat = []
                st.session_state.mock_feedback = []
                st.session_state.mock_scores = ""
                st.session_state.mock_started = False

                st.success("Mock interview reset.")
                st.rerun()

        if st.session_state.mock_started:

            if interview_mode == "Text Interview":

                for message in st.session_state.mock_chat:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

            else:

                latest_assistant_message = None

                for message in reversed(st.session_state.mock_chat):
                    if message["role"] == "assistant":
                        latest_assistant_message = message["content"]
                        break

                if latest_assistant_message:

                    st.markdown("### 🎤 Voice Interview Mode")
                    st.info("Step 1: Listen to the AI interviewer.")

                    audio_path = "latest_question.mp3"

                    mock_interview_agent.generate_ai_voice(
                        latest_assistant_message,
                        audio_path
                    )

                    st.audio(
                        audio_path,
                        format="audio/mp3"
                    )

            user_answer = None

            if interview_mode == "Text Interview":

                user_answer = st.chat_input(
                    "Type your interview answer..."
                )

            else:

                st.markdown("### 🎙️ Your Turn")

                audio = mic_recorder(
                    start_prompt="🎙️ Start Answer",
                    stop_prompt="⏹️ Stop Answer",
                    key="voice_recorder"
                )

                if audio:
                    if st.button("Submit Voice Answer", use_container_width=True):

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=".wav"
                        ) as tmp_file:

                            tmp_file.write(audio["bytes"])
                            tmp_audio_path = tmp_file.name

                        with st.spinner("🎧 Processing your response..."):

                            user_answer = mock_interview_agent.transcribe_audio(
                                tmp_audio_path
                            )

            if user_answer:

                st.session_state.mock_chat.append(
                    {
                        "role": "user",
                        "content": user_answer
                    }
                )

                conversation_history = []

                for i in range(
                    0,
                    len(st.session_state.mock_chat) - 1,
                    2
                ):

                    if (
                        i + 1 < len(st.session_state.mock_chat)
                        and st.session_state.mock_chat[i]["role"] == "assistant"
                        and st.session_state.mock_chat[i + 1]["role"] == "user"
                    ):

                        conversation_history.append(
                            {
                                "interviewer": st.session_state.mock_chat[i]["content"],
                                "candidate": st.session_state.mock_chat[i + 1]["content"]
                            }
                        )

                with st.spinner("Generating feedback for your answer..."):

                    feedback = mock_interview_agent.evaluate_answer(
                        st.session_state.mock_chat[-2]["content"],
                        user_answer,
                        st.session_state.resume_text,
                        job_description
                    )

                st.session_state.mock_feedback.append(
                    {
                        "question": st.session_state.mock_chat[-2]["content"],
                        "answer": user_answer,
                        "feedback": feedback
                    }
                )

                st.session_state.mock_scores = ""

                with st.spinner("🎤 AI interviewer is thinking..."):

                    next_question = mock_interview_agent.interviewer_chat(
                        st.session_state.resume_text,
                        job_description,
                        conversation_history
                    )

                st.session_state.mock_chat.append(
                    {
                        "role": "assistant",
                        "content": next_question
                    }
                )

                st.rerun()

            if st.session_state.mock_feedback:

                st.markdown("---")
                st.subheader("📊 Interview Feedback")

                for item in reversed(st.session_state.mock_feedback):

                    with st.expander(item["question"]):

                        st.write("Your Answer:")
                        st.write(item["answer"])

                        st.write("Feedback:")
                        st.write(item["feedback"])

                st.markdown("---")
                st.subheader("📈 Final Interview Analytics")

                if len(st.session_state.mock_feedback) < 3:

                    st.info(
                        "Complete at least 3 interview questions to generate accurate interview analytics."
                    )

                else:

                    if st.button(
                        "Generate Final Interview Analytics",
                        use_container_width=True
                    ):

                        with st.spinner(
                            "Analyzing your full interview performance..."
                        ):

                            st.session_state.mock_scores = mock_interview_agent.generate_scores(
                                st.session_state.mock_feedback
                            )
                            save_mock_interview(
                                st.session_state.username,
                                {
                                    "chat": st.session_state.mock_chat,
                                    "feedback": st.session_state.mock_feedback,
                                    "scores": st.session_state.mock_scores
                                }
                            )

                    if st.session_state.mock_scores:

                        st.text_area(
                            "Interview Analytics Report",
                            st.session_state.mock_scores,
                            height=250
                        )
                        st.markdown("---")
                        st.subheader("📁 Saved Mock Interviews")
                        saved_interviews = load_mock_interviews(
                            st.session_state.username
                        )
                        
                        if len(saved_interviews) == 0:
                            
                            st.info("No saved mock interviews yet.")
                            
                        else:
                            for idx, interview in enumerate(
                                reversed(saved_interviews)
                            ):
                                with st.expander(
                                    f"Saved Interview {idx + 1}"
                                ):
                                    st.write("### Final Analytics")
                                    
                                    st.write(interview["scores"])
                                    
                                    st.write("### Feedback History")
                                    
                                    for item in interview["feedback"]:
                                        
                                        st.write("Question:")
                                        st.write(item["question"])
                                        
                                        st.write("Your Answer:")
                                        st.write(item["answer"])
                                        
                                        st.write("Feedback:")
                                        st.write(item["feedback"])
                                        
                                        st.markdown("---")

        else:

            st.info("Click Start Interview to begin your AI mock interview.")
        

elif page == "📌 Tracker":

    st.header("📌 Application Tracker")

    col1, col2 = st.columns(2)

    with col1:

        company = st.text_input("Company Name")

        role = st.text_input("Role Title")

        job_link = st.text_input("Job Link")

    with col2:

        status = st.selectbox(
            "Application Status",
            [
                "Interested",
                "Applied",
                "Interview",
                "Rejected",
                "Offer"
            ]
        )

        notes = st.text_area("Notes")

    if st.button(
        "Save Application",
        use_container_width=True
    ):

        missing_fields = []

        if company.strip() == "":
            missing_fields.append("Company Name")

        if role.strip() == "":
            missing_fields.append("Role Title")

        if job_link.strip() == "":
            missing_fields.append("Job Link")

        if len(missing_fields) > 0:

            st.warning(
                "Please fill: " + ", ".join(missing_fields)
            )

        else:

            saved = save_application(
                st.session_state.username,
                company,
                role,
                job_link,
                status,
                notes
            )

            if saved:
                st.success(
                    "Application saved successfully!"
                )

            else:
                st.warning(
                    "This application is already saved."
                )

    applications = load_applications(
        st.session_state.username
    )

    if not applications.empty:

        st.markdown("---")

        st.header("📊 Application Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Applications",
                len(applications)
            )

        with col2:

            applied_count = len(
                applications[
                    applications["status"] == "Applied"
                ]
            )

            st.metric(
                "Applied",
                applied_count
            )

        with col3:

            interview_count = len(
                applications[
                    applications["status"] == "Interview"
                ]
            )

            st.metric(
                "Interviews",
                interview_count
            )

        status_counts = (
            applications["status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "Status",
            "Count"
        ]

        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Applications by Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Saved Applications")

        st.dataframe(
            applications,
            use_container_width=True
        )

        st.markdown("### Manage Applications")

        for idx, row in applications.iterrows():

            st.markdown("---")

            col1, col2, col3 = st.columns([5, 2, 1])

            with col1:

                st.write(
                    f"🏢 {row['company']}"
                )

                st.write(
                    f"💼 {row['role']}"
                )

                st.write(
                    f"📍 Status: {row['status']}"
                )

            with col2:

                new_status = st.selectbox(
                    "Update Status",
                    [
                        "Interested",
                        "Applied",
                        "Interview",
                        "Rejected",
                        "Offer"
                    ],
                    index=[
                        "Interested",
                        "Applied",
                        "Interview",
                        "Rejected",
                        "Offer"
                    ].index(row["status"]),
                    key=f"status_{idx}"
                )

                if new_status != row["status"]:

                    update_application_status(
                        st.session_state.username,
                        idx,
                        new_status
                    )

                    st.success("Status updated!")

                    st.rerun()

                if new_status == "Interview":

                    interview_date = st.date_input(
                        "Interview Date",
                        key=f"interview_date_{idx}"
                    )

                    if st.button(
                        "Save Interview Date",
                        key=f"save_interview_{idx}"
                    ):

                        update_interview_date(
                            st.session_state.username,
                            idx,
                            str(interview_date)
                        )

                        st.success(
                            "Interview date updated!"
                        )

                        st.rerun()

            with col3:

                if st.button(
                    "Delete",
                    key=f"delete_{idx}"
                ):

                    delete_application(
                        st.session_state.username,
                        idx
                    )

                    st.success(
                        "Application deleted successfully!"
                    )

                    st.rerun()

        csv_data = applications.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Applications CSV",
            data=csv_data,
            file_name=f"{st.session_state.username}_applications.csv",
            mime="text/csv"
        )
