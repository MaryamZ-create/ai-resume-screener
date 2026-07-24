import os
import json
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-flash-latest")


def create_prompt(resume_text: str, job_description: str):

    prompt = f"""
You are an AI resume screening assistant.

Compare the resume with the job description.

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY valid JSON.
Do not add explanations or markdown.

The JSON must follow this exact format:

{{
    "match_score": number between 0 and 100,
    "missing_keywords": [],
    "suggestions": []
}}
"""

    return prompt


def analyze_resume(resume_text: str, job_description: str):

    prompt = create_prompt(
        resume_text,
        job_description
    )

    response = model.generate_content(prompt)

    result = response.text.strip()

    try:
        return json.loads(result)

    except json.JSONDecodeError:
        return {
            "match_score": 0,
            "missing_keywords": [],
            "suggestions": [
                "Gemini returned invalid JSON"
            ]
        }
