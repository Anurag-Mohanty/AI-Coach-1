try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
try:
    import docx
except ImportError:
    docx = None
import io
import re

def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'pdf':
        raw_text = parse_pdf(uploaded_file)
    elif file_type == 'docx':
        raw_text = parse_docx(uploaded_file)
    elif file_type == 'txt':
        raw_text = uploaded_file.read().decode('utf-8')
    else:
        return "Unsupported file type. Please upload a PDF, DOCX, or TXT file."

    cleaned = normalize_resume_text(raw_text)
    # Remove sensitive info while preserving key data
    cleaned = remove_personally_identifiable_info(cleaned, 
                                   redact_names=False,  # Disable name redaction
                                   redact_emails=True,
                                   redact_phone=True,
                                   redact_address=True)
    return cleaned

def parse_pdf(file):
    text = ""
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error parsing PDF: {e}"

def parse_docx(file):
    text = ""
    try:
        doc = docx.Document(io.BytesIO(file.read()))
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error parsing DOCX: {e}"

def normalize_resume_text(text):
    # Basic text normalization
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_personally_identifiable_info(text, redact_names=False, redact_emails=False, redact_phone=False, redact_address=False):
    """Remove PII with simpler regex patterns"""
    if redact_emails:
        text = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', text)

    if redact_phone:
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    if redact_address:
        text = re.sub(r'\d+\s+[A-Za-z\s]+(St|Ave|Rd|Blvd|Dr|Lane)\b', '[ADDRESS]', text, flags=re.IGNORECASE)

    if redact_names:
        # Simplified name detection
        text = re.sub(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NAME]', text)

    return text