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
    InterviewCoachAgent
)

from tracker import save_application, load_applications


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
st.sidebar.write("✅ Recruiter Message Agent")
st.sidebar.write("✅ Resume Tailoring Agent")
st.sidebar.write("✅ Interview Coach Agent")
st.sidebar.write("✅ Application Tracker")
st.sidebar.write("✅ Analytics Dashboard")

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

analyze_button = st.button(
    "🚀 Analyze Job",
    use_container_width=True
)

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if analyze_button:

    if resume_file is None:
        st.warning("Please upload your resume first.")

    elif job_description.strip() == "":
        st.warning("Please paste the job description.")

    else:
        with st.spinner("Resume Agent is reading your resume..."):
            st.session_state.resume_text = resume_agent.parse_resume(
                resume_file
            )

        with st.spinner("ATS Agent is analyzing job match..."):
            st.session_state.analysis = ats_agent.analyze(
                st.session_state.resume_text,
                job_description
            )

        st.success("Multi-agent analysis completed successfully!")

tabs = st.tabs([
    "📊 Match Dashboard",
    "🎯 Job Recommendations",
    "✍️ Cover Letter",
    "💬 Recruiter Message",
    "📝 Resume Tailor",
    "🎤 Interview Coach",
    "📌 Tracker"
])

with tabs[0]:

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

        with st.expander("View Extracted Resume Text"):
            st.text_area(
                "Resume Content",
                st.session_state.resume_text,
                height=300
            )

with tabs[1]:

    st.header("🎯 AI Job Recommendation Engine")

    if st.session_state.resume_text == "":
        st.info("Upload your resume and click Analyze Job first.")

    else:
        if st.button("Generate Job Recommendations", use_container_width=True):

            with st.spinner("Recommendation Agent is finding best matching roles..."):
                recommendations = recommendation_agent.recommend(
                    st.session_state.resume_text
                )

            for item in recommendations["recommended_roles"]:

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

with tabs[2]:

    st.header("✍️ Tailored Cover Letter")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate a cover letter.")

    else:
        if st.button("Generate Cover Letter", use_container_width=True):

            with st.spinner("Cover Letter Agent is writing your letter..."):
                cover_letter = cover_letter_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

            st.text_area("Cover Letter", cover_letter, height=350)

            st.download_button(
                label="Download Cover Letter",
                data=cover_letter,
                file_name="cover_letter.txt",
                mime="text/plain"
            )

with tabs[3]:

    st.header("💬 LinkedIn Recruiter Message")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate a recruiter message.")

    else:
        if st.button("Generate Recruiter Message", use_container_width=True):

            with st.spinner("Recruiter Agent is generating your message..."):
                recruiter_message = recruiter_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

            st.text_area("Recruiter Message", recruiter_message, height=250)

            st.download_button(
                label="Download Recruiter Message",
                data=recruiter_message,
                file_name="recruiter_message.txt",
                mime="text/plain"
            )

with tabs[4]:

    st.header("📝 Resume Tailoring Agent")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate tailored resume improvements.")

    else:
        if st.button("Generate Resume Improvements", use_container_width=True):

            with st.spinner("Resume Tailor Agent is optimizing your resume..."):
                tailored_resume = resume_tailor_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

            st.text_area(
                "Tailored Resume Improvements",
                tailored_resume,
                height=450
            )

            st.download_button(
                label="Download Resume Improvements",
                data=tailored_resume,
                file_name="tailored_resume_improvements.txt",
                mime="text/plain"
            )

with tabs[5]:

    st.header("🎤 AI Interview Coach")

    if st.session_state.resume_text == "" or job_description.strip() == "":
        st.info("Analyze a job first to generate interview questions.")

    else:
        if st.button("Generate Interview Questions", use_container_width=True):

            with st.spinner("Interview Coach Agent is preparing questions..."):
                interview_questions = interview_agent.generate(
                    st.session_state.resume_text,
                    job_description
                )

            st.text_area(
                "Interview Preparation",
                interview_questions,
                height=500
            )

            st.download_button(
                label="Download Interview Questions",
                data=interview_questions,
                file_name="interview_questions.txt",
                mime="text/plain"
            )

with tabs[6]:

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
        save_application(company, role, job_link, status, notes)
        st.success("Application saved successfully!")

    applications = load_applications()

    if not applications.empty:
        st.markdown("---")
        st.subheader("📊 Application Analytics")

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

        status_counts = applications["status"].value_counts().reset_index()
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
        
