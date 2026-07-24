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
    "missing_keywords": [
        "keyword1",
        "keyword2"
    ],
    "suggestions": [
        "suggestion1",
        "suggestion2"
    ]
}}
"""

    return prompt