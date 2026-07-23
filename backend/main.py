from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from resume_parser import extract_text_from_pdf, extract_text_from_docx
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

    # Save resume text for analysis
    resume_data["filename"] = file.filename
    resume_data["text"] = text

    return {
        "filename": file.filename,
        "text": text
    }


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