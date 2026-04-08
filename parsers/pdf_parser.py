import pdfplumber

def parse(file_path: str) -> str:
    all_text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text.append(text.strip())
    return "\n".join(all_text)