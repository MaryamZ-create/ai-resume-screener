from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from resume_parser import extract_text_from_pdf, extract_text_from_docx
import shutil


app = FastAPI()


# Temporary storage for job description
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