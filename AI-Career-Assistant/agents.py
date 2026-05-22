from resume_parser import extract_resume_text
from job_analyzer import analyze_job_match
from cover_letter import generate_cover_letter
from recruiter_message import generate_recruiter_message
from resume_tailor import generate_tailored_resume_points
from interview_coach import generate_interview_questions
from job_recommender import recommend_jobs
from career_chatbot import career_chatbot_response


class ResumeAgent:
    def parse_resume(self, file):
        return extract_resume_text(file)


class ATSAgent:
    def analyze(self, resume_text, job_description):
        return analyze_job_match(resume_text, job_description)


class RecommendationAgent:
    def recommend(self, resume_text):
        return recommend_jobs(resume_text)


class CoverLetterAgent:
    def generate(self, resume_text, job_description):
        return generate_cover_letter(resume_text, job_description)


class RecruiterAgent:
    def generate(self, resume_text, job_description):
        return generate_recruiter_message(resume_text, job_description)


class ResumeTailorAgent:
    def generate(self, resume_text, job_description):
        return generate_tailored_resume_points(resume_text, job_description)


class InterviewCoachAgent:
    def generate(self, resume_text, job_description):
        return generate_interview_questions(resume_text, job_description)
    
class CareerCoachAgent:
    def chat(self, resume_text, chat_history, user_question):
        return career_chatbot_response(
            resume_text,
            chat_history,
            user_question
        )
