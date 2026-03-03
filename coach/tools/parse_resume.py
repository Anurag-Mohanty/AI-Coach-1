"""
parse_resume tool — wraps existing resume_parser + resume_utils.
Accepts file bytes + filename OR raw text. Returns a clean structured profile.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from tools.resume.resume_parser import (
    extract_text_from_file,
)
from tools.resume.resume_utils import extract_all_fields


class _UploadedFileCompat:
    """Minimal file-like object that satisfies resume_parser's expectations."""

    def __init__(self, content: bytes, filename: str):
        self._content = content
        self.name = filename

    def read(self) -> bytes:
        return self._content


def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """
    Extract a structured profile from a resume file.
    Input:  raw file bytes + filename (PDF, DOCX, or TXT)
    Output: structured profile dict
    """
    fake_file = _UploadedFileCompat(file_bytes, filename)
    text = extract_text_from_file(fake_file)

    if text.startswith("Error") or text.startswith("Unsupported"):
        return {"error": text}

    return _fields_to_profile(extract_all_fields(text))


def parse_resume_from_text(resume_text: str) -> dict:
    """
    Extract a structured profile from pasted resume text.
    Input:  raw text string
    Output: structured profile dict
    """
    return _fields_to_profile(extract_all_fields(resume_text))


def _fields_to_profile(fields: dict) -> dict:
    return {
        "title": fields.get("title", ""),
        "seniority": fields.get("seniority", ""),
        "company": fields.get("company_name", ""),
        "company_size": fields.get("company_size", ""),
        "domain": fields.get("domain", ""),
        "years_experience": fields.get("years_experience"),
        "skills": fields.get("skills", []),
        "tools_known": fields.get("tools", []),
        "ai_tools_known": fields.get("ai_keywords", []),
        "education": fields.get("education", []),
    }
