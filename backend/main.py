from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class JobDescription(BaseModel):
    description: str


@app.get("/")
def home():
    return {"message": "AI Resume Screener API is running"}


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "message": "Resume uploaded successfully"}


@app.post("/analyze/")
def analyze_resume(job: JobDescription):
    return {
        "score": 75,
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": ["Docker", "Kubernetes"],
        "message": "Basic analysis complete"
    }
