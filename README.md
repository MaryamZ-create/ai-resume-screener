# AI Resume Screener

An AI-powered resume screening application that compares a candidate's resume with a job description and provides a match score, missing skills, and improvement suggestions.

## Features

- Upload PDF/DOCX resumes
- Extract resume text automatically
- Analyze resumes against job descriptions using Google Gemini AI
- Generate:
  - Resume match score
  - Missing keywords
  - Improvement suggestions
- Streamlit user interface
- FastAPI backend
- Error handling for AI API failures

## Tech Stack

### Backend

- Python
- FastAPI
- Uvicorn
- Google Gemini API

### Frontend

- Streamlit

### Libraries

- python-docx
- pypdf
- requests
- python-dotenv

## Project Structure

```
ai-resume-screener/
│
├── backend/
│   ├── main.py
│   ├── ai_analyzer.py
│   └── resume_parser.py
│
├── uploads/
│   └── sample_resume.docx
│
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
BACKEND_URL=http://localhost:8000
```

Replace `your_gemini_api_key` with your actual Gemini API key.

## Running the Application

### Start FastAPI Backend

Run:

```bash
uvicorn backend.main:app --reload
```

Backend will run at:

```
http://localhost:8000
```

### Start Streamlit Frontend

Open another terminal and run:

```bash
streamlit run app.py
```

Frontend will run at:

```
http://localhost:8501
```

## How It Works

1. Upload a resume in PDF or DOCX format.
2. The backend extracts resume text.
3. Enter a job description.
4. Gemini AI compares the resume with the job requirements.
5. The application displays:
   - Match score
   - Missing keywords
   - Improvement suggestions

## API Endpoints

### Upload Resume

```
POST /upload-resume/
```

Accepts:

- PDF files
- DOCX files

### Analyze Resume

```
POST /analyze/
```

Example request:

```json
{
  "description": "Looking for a Python developer with FastAPI, Docker, AWS and REST API experience."
}
```

Example response:

```json
{
  "match_score": 70,
  "missing_keywords": [
    "Docker",
    "AWS"
  ],
  "suggestions": [
    "Add Docker experience",
    "Include AWS projects"
  ]
}
```

## Future Improvements

- User authentication
- Resume history storage
- Multiple resume comparison
- Database integration
- Cloud deployment
- Better AI scoring system

## License

MIT License