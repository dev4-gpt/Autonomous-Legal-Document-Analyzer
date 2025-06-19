import os
import fitz  # PyMuPDF
import docx
from bs4 import BeautifulSoup

SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.html']

def parse_contract(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return parse_pdf(file_path)
    elif ext == '.docx':
        return parse_docx(file_path)
    elif ext == '.txt':
        return parse_txt(file_path)
    elif ext == '.html':
        return parse_html(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def parse_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()

def parse_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

def parse_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().strip()

def parse_html(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        soup = BeautifulSoup(f, 'html.parser')
        return soup.get_text(separator='\n').strip() 