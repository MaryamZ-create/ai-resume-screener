from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.resume_parser import extract_text_from_pdf, extract_text_from_docx
from backend.document_parser import (
    extract_text_from_pdf as extract_document_pdf,
    extract_text_from_txt
)
from backend.chunker import chunk_text
import shutil
from backend.chunker import chunk_text
from backend.embeddings import generate_embedding
from backend.qdrant_db import create_collection, store_chunks, search_chunks


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
# -------------------------------
# STUDY FLASHCARDS
# -------------------------------

@app.post("/flashcards")
def flashcards():

    if "study_chunks" not in resume_data:
        return {
            "error": "No study document uploaded"
        }

    chunks = resume_data["study_chunks"]

    flashcards = []

    for i, chunk in enumerate(chunks, 1):

        flashcards.append({
            "question": f"What should you remember from study chunk {i}?",
            "answer": chunk
        })

    return {
        "flashcards": flashcards
    }
# -------------------------------
# STUDY QUIZ
# -------------------------------

@app.post("/quiz")
def quiz():

    if "study_text" not in resume_data:
        return {
            "error": "No study document uploaded"
        }

    text = resume_data["study_text"].lower()

    questions = []

    if "tcp" in text and "udp" in text:
        questions.append({
            "question": "Which protocol is connection-oriented?",
            "options": [
                "A. UDP",
                "B. TCP",
                "C. DNS",
                "D. HTTP"
            ],
            "answer": "B. TCP"
        })

        questions.append({
            "question": "Which protocol is connectionless?",
            "options": [
                "A. TCP",
                "B. FTP",
                "C. UDP",
                "D. SSH"
            ],
            "answer": "C. UDP"
        })

    return {
        "quiz": questions
    }
# -------------------------------
# WEEK 3: INGEST DOCUMENT
# -------------------------------

@app.post("/ingest-document")
def ingest_document():

    study_text = resume_data.get("study_text", "")

    if not study_text:
        return {
            "error": "No study document uploaded"
        }

    chunks = chunk_text(study_text, max_words=300)

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    create_collection()
    store_chunks(chunks, embeddings)

    resume_data["study_chunks"] = chunks

    return {
        "message": "Document successfully embedded and stored in Qdrant",
        "chunks_stored": len(chunks),
        "embedding_dimension": len(embeddings[0])
    }


# -------------------------------
# WEEK 3: RETRIEVAL
# -------------------------------

@app.post("/retrieve")
def retrieve(topic: str):

    embedding = generate_embedding(topic)

    results = search_chunks(embedding, limit=3)

    return {
        "query": topic,
        "results": results
    }


# -------------------------------
# WEEK 3: BASIC STUDY PLAN
# -------------------------------

@app.post("/study-plan")
def study_plan(topic: str):

    embedding = generate_embedding(topic)

    results = search_chunks(embedding, limit=3)

    if not results:
        return {
            "error": "No relevant study material found"
        }

    plan = []

    for i, result in enumerate(results, 1):
        plan.append({
            "step": i,
            "topic": topic,
            "duration_minutes": 20,
            "material": result["text"]
        })

    return {
        "topic": topic,
        "study_plan": plan,
        "retrieved_chunks": len(results)
    }
# -------------------------------
# WEEK 3: INGEST DOCUMENT
# -------------------------------

@app.post("/ingest-document")
def ingest_document():

    study_text = resume_data.get("study_text", "")

    if not study_text:
        return {
            "error": "No study document uploaded"
        }

    chunks = chunk_text(study_text, max_words=300)

    embeddings = [
        generate_embedding(chunk)
        for chunk in chunks
    ]

    create_collection()
    store_chunks(chunks, embeddings)

    resume_data["study_chunks"] = chunks

    return {
        "message": "Document successfully embedded and stored in Qdrant",
        "chunks_stored": len(chunks),
        "embedding_dimension": len(embeddings[0])
    }


# -------------------------------
# WEEK 3: RETRIEVAL
# -------------------------------

@app.post("/retrieve")
def retrieve(topic: str):

    embedding = generate_embedding(topic)

    results = search_chunks(embedding, limit=3)

    return {
        "query": topic,
        "results": results
    }


# -------------------------------
# WEEK 3: BASIC STUDY PLAN
# -------------------------------

@app.post("/study-plan")
def study_plan(topic: str):

    embedding = generate_embedding(topic)

    results = search_chunks(embedding, limit=3)

    if not results:
        return {
            "error": "No relevant study material found"
        }

    plan = []

    for i, result in enumerate(results, 1):
        plan.append({
            "step": i,
            "topic": topic,
            "duration_minutes": 20,
            "material": result["text"]
        })

    return {
        "topic": topic,
        "study_plan": plan,
        "retrieved_chunks": len(results)
    }
