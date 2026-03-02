from pathlib import Path
import pypdf, docx

DOCS_PATH = Path("./../documents")

def load_documents():
    docs = []
    for f in DOCS_PATH.iterdir():
        if f.suffix == ".pdf":
            reader = pypdf.PdfReader(str(f))
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
        elif f.suffix == ".docx":
            d = docx.Document(str(f))
            text = "\n".join(p.text for p in d.paragraphs)
        elif f.suffix == ".txt":
            text = f.read_text(encoding="utf-8")
        else:
            continue
        docs.append({"source": f.name, "content": text})
    return docs