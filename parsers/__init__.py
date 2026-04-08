import os
from parsers import txt_parser, docx_parser, pdf_parser, auto_parser

AUTO_EXTENSIONS = {".vtt", ".srt"}

def load(file_path: str) -> str:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        return txt_parser.parse(file_path)
    elif ext == ".docx":
        return docx_parser.parse(file_path)
    elif ext == ".pdf":
        return pdf_parser.parse(file_path)
    elif ext in AUTO_EXTENSIONS:
        return auto_parser.parse(file_path)
    else:
        # Try auto parser as fallback for unknown text-like files
        try:
            return auto_parser.parse(file_path)
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}")