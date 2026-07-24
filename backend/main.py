from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

from backend.resume_parser import extract_text_from_pdf, extract_text_from_docx
from backend.ai_analyzer import analyze_resume

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

resume_text_storage = ""


class JobDescription(BaseModel):
    description: str


@app.get("/")
def home():
    return {"message": "AI Resume Screener API is running"}


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    global resume_text_storage

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.endswith(".pdf"):
        resume_text_storage = extract_text_from_pdf(file_path)

    elif file.filename.endswith(".docx"):
        resume_text_storage = extract_text_from_docx(file_path)

    else:
        return {
            "error": "Only PDF and DOCX files are supported"
        }

    return {
        "filename": file.filename,
        "message": "Resume uploaded successfully",
        "text_length": len(resume_text_storage)
    }


@app.post("/analyze/")
def analyze_resume_endpoint(job: JobDescription):

    if not resume_text_storage:
        return {
            "error": "Please upload a resume first"
        }

    result = analyze_resume(
        resume_text_storage,
        job.description
    )

    return result