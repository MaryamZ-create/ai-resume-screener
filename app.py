import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="centered"
)

st.title("📄 AI Resume Screener")
st.write(
    "Upload your resume and compare it with a job description using AI."
)

st.divider()

# Resume upload
uploaded_file = st.file_uploader(
    "Upload Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

# Job description
job_description = st.text_area(
    "Paste Job Description",
    height=200,
    placeholder="Example: We need a Python developer with FastAPI, Docker, AWS..."
)


# Upload resume
if uploaded_file:

    if st.button("📤 Upload Resume"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/upload-resume/",
                files=files
            )

            if response.status_code == 200:
                data = response.json()

                st.success(
                    "Resume uploaded successfully!"
                )

                st.write(
                    f"File: {data['filename']}"
                )

                st.write(
                    f"Extracted text length: {data['text_length']} characters"
                )

            else:
                st.error(response.text)

        except Exception as e:
            st.error(
                f"Backend connection error: {e}"
            )


st.divider()


# Analyze resume
if st.button("🤖 Analyze Resume"):

    if not job_description.strip():
        st.warning(
            "Please enter a job description first."
        )

    else:

        try:

            response = requests.post(
                f"{BACKEND_URL}/analyze/",
                json={
                    "description": job_description
                }
            )

            if response.status_code == 200:

                result = response.json()

                score = result.get(
                    "match_score",
                    0
                )

                st.subheader(
                    "Resume Match Score"
                )

                st.progress(
                    score / 100
                )

                st.metric(
                    "Match Score",
                    f"{score}%"
                )


                st.divider()


                st.subheader(
                    "⚠️ Missing Keywords"
                )

                missing = result.get(
                    "missing_keywords",
                    []
                )

                if missing:

                    for item in missing:
                        st.warning(item)

                else:
                    st.success(
                        "No missing keywords found!"
                    )


                st.divider()


                st.subheader(
                    "💡 Suggestions"
                )

                suggestions = result.get(
                    "suggestions",
                    []
                )

                for item in suggestions:
                    st.info(item)


            else:

                st.error(
                    response.text
                )


        except Exception as e:

            st.error(
                f"Backend connection error: {e}"
            )