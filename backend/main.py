from fastapi import FastAPI, UploadFile, File
from resume_parser import extract_text_from_pdf, extract_text_from_docx
import shutil


app = FastAPI()


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