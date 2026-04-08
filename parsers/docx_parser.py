from docx import Document

def parse(file_path: str) -> str:
    doc = Document(file_path)
    lines = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(lines)