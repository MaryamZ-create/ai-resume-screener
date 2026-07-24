import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You analyze resumes and return JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    return json.loads(result)