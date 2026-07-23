from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_path):
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_text_from_docx(file_path):
    text = ""

    doc = Document(file_path)

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text