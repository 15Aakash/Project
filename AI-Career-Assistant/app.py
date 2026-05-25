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


st.set_page_config(
    page_title="AI Career Assistant",
    layout="wide",
    page_icon="🤖"
)

st.sidebar.title("🤖 AI Career Assistant")
st.sidebar.write("### Features")
st.sidebar.write("✅ Resume Parser Agent")
st.sidebar.write("✅ ATS Match Agent")
st.sidebar.write("✅ Job Recommendation Agent")
st.sidebar.write("✅ Cover Letter Agent")
st.sidebar.write("✅ Recruiter Outreach Agent")
st.sidebar.write("✅ Resume Tailoring Agent")
st.sidebar.write("✅ Interview Coach Agent")
st.sidebar.write("✅ AI Career Coach with Memory")
st.sidebar.write("✅ Application Tracker")
st.sidebar.write("✅ Analytics Dashboard")
st.sidebar.write("✅ PDF Export")

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

if "mock_history" not in st.session_state:
    st.session_state.mock_history = []

if "current_mock_question" not in st.session_state:
    st.session_state.current_mock_question = ""

if "mock_chat" not in st.session_state:
    st.session_state.mock_chat = []

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

if st.button("🚀 Analyze Job", use_container_width=True):

    if resume_file is None:
        st.warning("Please upload your resume first.")

    elif job_description.strip() == "":
        st.warning("Please paste the job description.")

    else:
        with st.spinner("Resume Agent is reading your resume..."):
            st.session_state.resume_text = resume_agent.parse_resume(resume_file)

        with st.spinner("ATS Agent is analyzing job match..."):
            st.session_state.analysis = ats_agent.analyze(
                st.session_state.resume_text,
                job_description
            )

        st.success("Multi-agent analysis completed successfully!")

st.markdown("---")

page = st.radio(
    "Navigation",
    [
        "📊 Match Dashboard",
        "🎯 Job Recommendations",
        "✍️ Cover Letter",
        "💬 Recruiter Outreach",
        "📝 Resume Tailor",
        "🎤 Interview Coach",
        "💬 AI Career Coach",
        "🎙️ Mock Interview",
        "📌 Tracker"
        
    ],
    horizontal=True
)

if page == "📊 Match Dashboard":

    st.header("📊 AI Job Match Dashboard")

    if st.session_state.analysis is None:
        st.info("Upload your resume, paste a job description, and click Analyze Job.")

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

elif page == "🎯 Job Recommendations":

    st.header("🎯 AI Job Recommendation Engine")

    if st.session_state.resume_text == "":
        st.info("Upload your resume and click Analyze Job first.")

    else:
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
                st.session_state.cover_letter = cover_letter_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

        if st.session_state.cover_letter:

            edited_cover_letter = st.text_area(
                "Edit Cover Letter Before Download",
                st.session_state.cover_letter,
                height=350
            )

            st.download_button(
                label="Download Edited Cover Letter as TXT",
                data=edited_cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )

            pdf_path = create_pdf(
                "",
                edited_cover_letter,
                "cover_letter.pdf"
            )

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Edited Cover Letter as PDF",
                    data=pdf_file,
                    file_name="cover_letter.pdf",
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

elif page == "📝 Resume Tailor":

    st.header("📝 Resume Tailoring Agent")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate tailored resume improvements.")

    else:
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

elif page == "💬 AI Career Coach":

    st.header("💬 AI Career Coach")

    if st.session_state.resume_text == "":
        st.info("Upload your resume and click Analyze Job first.")

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

        typed_question = st.chat_input("Ask your career coach...")

        if typed_question:
            user_question = typed_question

        if user_question:
            with st.spinner("Career Coach Agent is thinking..."):
                coach_answer = career_coach_agent.chat(
                    st.session_state.resume_text,
                    st.session_state.coach_history,
                    user_question
                )

            st.session_state.coach_history.append({
                "question": user_question,
                "answer": coach_answer
            })

            st.rerun()

        if st.session_state.coach_history:
            st.markdown("---")

            for chat in st.session_state.coach_history:
                with st.chat_message("user"):
                    st.write(chat["question"])

                with st.chat_message("assistant"):
                    st.write(chat["answer"])

elif page == "🎙️ Mock Interview":

    st.header("🎙️ AI Mock Interview")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to start the mock interview.")

    else:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Start Interview", use_container_width=True):

                st.session_state.mock_chat = []
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
                st.session_state.mock_started = False
                st.success("Mock interview reset.")
                st.rerun()

        if st.session_state.mock_started:

            for message in st.session_state.mock_chat:

                with st.chat_message(message["role"]):
                    st.write(message["content"])

            user_answer = st.chat_input("Type your interview answer...")

            if user_answer:

                st.session_state.mock_chat.append(
                    {
                        "role": "user",
                        "content": user_answer
                    }
                )

                conversation_history = []

                for i in range(0, len(st.session_state.mock_chat) - 1, 2):

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

                with st.spinner("AI interviewer is responding..."):

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
            ["Interested", "Applied", "Interview", "Rejected", "Offer"]
        )

        notes = st.text_area("Notes")

    if st.button("Save Application", use_container_width=True):

        missing_fields = []

        if company.strip() == "":
            missing_fields.append("Company Name")

        if role.strip() == "":
            missing_fields.append("Role Title")

        if job_link.strip() == "":
            missing_fields.append("Job Link")

        if len(missing_fields) > 0:
            st.warning("Please fill: " + ", ".join(missing_fields))

        else:
            saved = save_application(
                company,
                role,
                job_link,
                status,
                notes
            )

            if saved:
                st.success("Application saved successfully!")
            else:
                st.warning("This application is already saved.")

    applications = load_applications()

    if not applications.empty:

        st.markdown("---")

        st.header("📊 Application Analytics")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Applications", len(applications))

        with col2:
            applied_count = len(
                applications[applications["status"] == "Applied"]
            )
            st.metric("Applied", applied_count)

        with col3:
            interview_count = len(
                applications[applications["status"] == "Interview"]
            )
            st.metric("Interviews", interview_count)

        if "interview_date" in applications.columns:

            upcoming = applications[
                applications["interview_date"].notna()
                & (applications["interview_date"] != "")
            ]

            if not upcoming.empty:
                st.subheader("📅 Upcoming Interviews")
                st.dataframe(
                    upcoming[
                        [
                            "company",
                            "role",
                            "interview_date",
                            "notes"
                        ]
                    ],
                    use_container_width=True
                )

        status_counts = (
            applications["status"]
            .value_counts()
            .reset_index()
        )

        status_counts.columns = ["Status", "Count"]

        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Applications by Status"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Saved Applications")

        st.dataframe(applications, use_container_width=True)

        st.markdown("### Manage Applications")

        for idx, row in applications.iterrows():

            col1, col2, col3, col4 = st.columns([4, 2, 2, 1])

            with col1:
                st.write(
                    f"{row['company']} | {row['role']}"
                )

            with col2:
                status_options = [
                    "Interested",
                    "Applied",
                    "Interview",
                    "Rejected",
                    "Offer"
                ]

                current_status = row["status"]

                if current_status not in status_options:
                    current_status = "Interested"

                new_status = st.selectbox(
                    "Update Status",
                    status_options,
                    index=status_options.index(current_status),
                    key=f"status_{idx}"
                )

                if new_status != row["status"]:
                    update_application_status(idx, new_status)
                    st.success("Status updated!")
                    st.rerun()
            with col3:

                if row["status"] == "Interview":

                    interview_date = st.date_input(
                        "Interview Date",
                        key=f"date_{idx}"
                    )

                    if st.button(
                        "Save Date",
                        key=f"save_date_{idx}"
                    ):

                        update_interview_date(
                            idx,
                            interview_date.strftime("%Y-%m-%d")
                        )

                        st.success("Interview date saved!")
                        st.rerun()

                else:
                    st.write("No interview scheduled")
        
            with col4:
                if st.button(
                    "Delete",
                    key=f"delete_{idx}"
                ):
                    delete_application(idx)
                    st.success("Application deleted successfully!")
                    st.rerun()

        csv_data = applications.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Applications CSV",
            data=csv_data,
            file_name="applications.csv",
            mime="text/csv"
        )
