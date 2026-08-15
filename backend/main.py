from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.resume_parser import extract_text_from_pdf, extract_text_from_docx
from backend.document_parser import (
    extract_text_from_pdf as extract_document_pdf,
    extract_text_from_txt
)
from backend.chunker import chunk_text
import shutil


app = FastAPI()


# Temporary storage
resume_data = {}
job_description_data = {}


class JobDescription(BaseModel):
    title: str
    description: str


@app.get("/")
def home():
    return {
        "message": "AI Resume Screener Backend Running"
    }


# -------------------------------
# RESUME UPLOAD
# -------------------------------

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

    elif file.filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)

    else:
        return {
            "error": "Only PDF and DOCX files are supported"
        }

    resume_data["filename"] = file.filename
    resume_data["text"] = text

    return {
        "filename": file.filename,
        "text": text
    }


# -------------------------------
# JOB DESCRIPTION
# -------------------------------

@app.post("/job-description")
def add_job_description(job: JobDescription):

    job_description_data["title"] = job.title
    job_description_data["description"] = job.description

    return {
        "message": "Job description saved",
        "job": job_description_data
    }


@app.get("/job-description")
def get_job_description():

    return {
        "job": job_description_data
    }


# -------------------------------
# RESUME ANALYSIS
# -------------------------------

@app.post("/analyze-resume")
def analyze_resume():

    resume_text = resume_data.get("text", "")
    job_text = job_description_data.get("description", "")

    if not resume_text:
        return {
            "error": "No resume uploaded"
        }

    if not job_text:
        return {
            "error": "No job description added"
        }

    skills = [
        "python",
        "fastapi",
        "javascript",
        "react",
        "sql",
        "machine learning",
        "docker",
        "aws"
    ]

    resume_lower = resume_text.lower()
    job_lower = job_text.lower()

    matched_skills = []

    for skill in skills:
        if skill in resume_lower and skill in job_lower:
            matched_skills.append(skill)

    missing_skills = []

    for skill in skills:
        if skill in job_lower and skill not in resume_lower:
            missing_skills.append(skill)

    required_skills = [
        skill for skill in skills
        if skill in job_lower
    ]

    if required_skills:
        score = int(
            (len(matched_skills) / len(required_skills)) * 100
        )
    else:
        score = 0

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }


# -------------------------------
# STUDY DOCUMENT UPLOAD
# -------------------------------

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):

    file_path = f"study_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        text = extract_document_pdf(file_path)

    elif file.filename.endswith(".txt"):
        text = extract_text_from_txt(file_path)

    else:
        return {
            "error": "Only PDF and TXT files are supported"
        }

    # Split study material into chunks
    chunks = chunk_text(text)

    # Save study material temporarily
    resume_data["study_text"] = text
    resume_data["study_chunks"] = chunks

    return {
        "filename": file.filename,
        "text": text,
        "chunks": chunks
    }


# -------------------------------
# STUDY QUESTIONS
# -------------------------------

@app.post("/study-questions")
def study_questions():

    if "study_text" not in resume_data:
        return {
            "error": "No study document uploaded"
        }

    chunks = resume_data["study_chunks"]

    questions = []

    for i, chunk in enumerate(chunks, 1):

        questions.append({
            "question": f"What is the main idea of study chunk {i}?",
            "answer": chunk
        })

    return {
        "questions": questions
    }