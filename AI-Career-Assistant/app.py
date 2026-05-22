import streamlit as st

from resume_parser import extract_resume_text
from job_analyzer import analyze_job_match
from cover_letter import generate_cover_letter
from recruiter_message import generate_recruiter_message
from resume_tailor import generate_tailored_resume_points
from tracker import save_application, load_applications
from interview_coach import generate_interview_questions

st.set_page_config(
    page_title="AI Career Assistant",
    layout="wide"
)

st.title("AI Career Assistant")

st.sidebar.title("AI Career Assistant")
st.sidebar.write("Features:")
st.sidebar.write("✅ Resume Parser")
st.sidebar.write("✅ ATS Match Score")
st.sidebar.write("✅ Cover Letter Generator")
st.sidebar.write("✅ Recruiter Message Generator")
st.sidebar.write("✅ Resume Tailoring Agent")
st.sidebar.write("✅ Application Tracker")
st.sidebar.write("✅ AI Interview Coach")

st.write(
    "AI-powered assistant for resume analysis, ATS job matching, and job application content generation."
)

resume_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"]
)

job_description = st.text_area(
    "Paste the job description here",
    height=250
)

if st.button("Analyze Job"):

    if resume_file is None:
        st.warning("Please upload your resume first.")

    elif job_description.strip() == "":
        st.warning("Please paste the job description.")

    else:
        with st.spinner("Reading resume..."):
            resume_text = extract_resume_text(resume_file)

        st.success("Resume successfully read!")

        with st.expander("View Extracted Resume Text"):
            st.text_area(
                "Resume Content",
                resume_text,
                height=300
            )

        with st.spinner("Analyzing ATS match..."):
            analysis = analyze_job_match(
                resume_text,
                job_description
            )

        st.markdown("---")
        st.header("AI Job Match Dashboard")

        st.metric("Match Score", analysis["match_score"])

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Strong Matching Skills")
            for skill in analysis["strong_skills"]:
                st.success(skill)

        with col2:
            st.subheader("Missing Skills")
            for skill in analysis["missing_skills"]:
                st.error(skill)

        st.subheader("ATS Keywords To Add")
        for keyword in analysis["keywords_to_add"]:
            st.info(keyword)

        st.subheader("Resume Improvements")
        for improvement in analysis["resume_improvements"]:
            st.warning(improvement)

        st.subheader("Final Decision")
        decision = analysis["final_decision"]

        if decision.upper() == "APPLY":
            st.success(decision)
        else:
            st.error(decision)

        st.subheader("Reason")
        st.write(analysis["reason"])

        st.markdown("---")

        with st.spinner("Generating cover letter..."):
            cover_letter = generate_cover_letter(
                resume_text,
                job_description
            )

        st.header("Tailored Cover Letter")

        st.text_area(
            "Cover Letter",
            cover_letter,
            height=300
        )

        st.download_button(
            label="Download Cover Letter",
            data=cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain"
        )

        st.markdown("---")

        with st.spinner("Generating recruiter message..."):
            recruiter_message = generate_recruiter_message(
                resume_text,
                job_description
            )

        st.header("LinkedIn Recruiter Message")

        st.text_area(
            "Recruiter Message",
            recruiter_message,
            height=200
        )

        st.download_button(
            label="Download Recruiter Message",
            data=recruiter_message,
            file_name="recruiter_message.txt",
            mime="text/plain"
        )

        st.markdown("---")

        with st.spinner("Generating tailored resume improvements..."):
            tailored_resume = generate_tailored_resume_points(
                resume_text,
                job_description
            )

        st.header("Tailored Resume Improvements")

        st.text_area(
            "Resume Improvements",
            tailored_resume,
            height=400
        )

        st.download_button(
            label="Download Tailored Resume Improvements",
            data=tailored_resume,
            file_name="tailored_resume_improvements.txt",
            mime="text/plain"
        )

st.markdown("---")
st.header("Application Tracker")

company = st.text_input("Company Name")
role = st.text_input("Role Title")
job_link = st.text_input("Job Link")

status = st.selectbox(
    "Application Status",
    ["Interested", "Applied", "Interview", "Rejected", "Offer"]
)

notes = st.text_area("Notes")

if st.button("Save Application"):
    save_application(company, role, job_link, status, notes)
    st.success("Application saved successfully!")

applications = load_applications()

if not applications.empty:
    st.subheader("Saved Applications")
    st.dataframe(applications)

st.markdown("---")
st.header("AI Interview Coach")

if resume_file is not None and job_description.strip() != "":

    if st.button("Generate Interview Questions"):

        resume_text = extract_resume_text(resume_file)

        with st.spinner("Generating interview questions..."):
            interview_questions = generate_interview_questions(
                resume_text,
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
else:
    st.info("Upload your resume and paste a job description to use the AI Interview Coach.")