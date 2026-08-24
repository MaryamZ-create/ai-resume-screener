from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.resume_parser import extract_text_from_pdf, extract_text_from_docx
from backend.chunker import chunk_text
from backend.embeddings import generate_embedding
from backend.qdrant_db import (
    create_collection,
    store_chunks,
    search_chunks,
)
import shutil


app = FastAPI()


# =========================
# EXISTING RESUME SCREENER
# =========================

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


# =========================
# WEEK 4 KNOWLEDGE BASE
# =========================

# Make sure the Qdrant collection exists
create_collection()


class KnowledgeQuery(BaseModel):
    query: str


@app.get("/knowledge")
def knowledge_status():

    return {
        "message": "Knowledge base is running",
        "collection": "study_documents"
    }


@app.post("/knowledge/search")
def knowledge_search(data: KnowledgeQuery):

    query_embedding = generate_embedding(data.query)

    results = search_chunks(
        query_embedding,
        limit=5
    )

    return {
        "query": data.query,
        "results": results
    }


@app.get("/knowledge/documents")
def knowledge_documents():

    from qdrant_client import QdrantClient

    client = QdrantClient(
        url="http://localhost:6333"
    )

    response = client.scroll(
        collection_name="study_documents",
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    points = response[0]

    documents = []

    for point in points:

        payload = point.payload or {}

        documents.append({
            "chunk_id": payload.get("chunk_id"),
            "text": payload.get("text", "")
        })

    return {
        "documents": documents
    }


@app.get("/knowledge/documents/{chunk_id}")
def get_knowledge_document(chunk_id: int):

    from qdrant_client import QdrantClient

    client = QdrantClient(
        url="http://localhost:6333"
    )

    result = client.retrieve(
        collection_name="study_documents",
        ids=[chunk_id],
        with_payload=True,
        with_vectors=False
    )

    if not result:
        return {
            "error": "Document not found"
        }

    point = result[0]
    payload = point.payload or {}

    return {
        "chunk_id": payload.get("chunk_id"),
        "text": payload.get("text", "")
    }
