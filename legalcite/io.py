"""Input reading. .txt/.md always; .pdf/.docx only if the optional
library is installed, otherwise a clear error (not a crash trace)."""

import os


def read_text_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md", ""):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception as e:
            raise ValueError(".pdf support needs pypdf (pip install pypdf)") from e
        reader = PdfReader(path)
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if ext == ".docx":
        try:
            from docx import Document  # type: ignore
        except Exception as e:
            raise ValueError(".docx support needs python-docx (pip install python-docx)") from e
        return "\n".join(p.text for p in Document(path).paragraphs)
    raise ValueError(f"unsupported file type: {ext or '(none)'}")
