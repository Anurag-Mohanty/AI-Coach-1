# compliance_utils.py
# Located in: /agent_core/
"""
🛡️ Compliance & Privacy Utilities
----------------------------------
Purpose: Ensure agents operate safely under data regulations (GDPR, CCPA, etc)
and reduce risk of storing or exposing personal information.

Used by:
- Resume Agent → Remove PII before storing feedback
- Role Context Agent → Hash input titles/companies
- Meta Agent → Track usage opt-in

"""

import re
import hashlib
import json
import os

PII_PATTERNS = [
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # emails
    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # phone numbers
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",  # uppercase variant emails
    r"[A-Z][a-z]+\s[A-Z][a-z]+",  # simple full names
]


def remove_personally_identifiable_info(text, redact_names=True, redact_emails=True, 
                                      redact_phone=True, redact_address=True,
                                      preserve_locations=False, preserve_institutions=False):
    """Removes PII from text with granular controls"""
    if redact_emails:
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    if redact_phone:
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

    if redact_names:
        # Redact full names while preserving titles
        text = re.sub(r'\b(?!Dr\.|Mr\.|Ms\.|Mrs\.|Prof\.)[A-Z][a-z]+\s+[A-Z][a-z]+\b', '[NAME]', text)

    if redact_address:
        # Redact street addresses but preserve city/state/country if needed
        text = re.sub(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\.?(?=[\s,])', '[ADDRESS]', text)

        if not preserve_locations:
            # Also redact city, state, zip if not preserving locations
            text = re.sub(r',\s*[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?', '[LOCATION]', text)

    return text


def hash_input_data(input_str: str) -> str:
    """
    Hash sensitive fields to store reference without storing PII
    """
    return hashlib.sha256(input_str.encode()).hexdigest()


def log_data_usage_consent(user_id: str, consent=True):
    """
    Track user consent for storing anonymized data (for training agents)
    """
    path = "logs/consent_log.jsonl"
    entry = {"user_id": user_id, "consent": consent}
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def forget_user_data(user_id: str):
    """
    Deletes user-specific data from context files
    """
    context_path = "logs/user_persona_context.json"
    if not os.path.exists(context_path):
        return
    with open(context_path, "r") as f:
        data = json.load(f)
    if user_id in data:
        del data[user_id]
        with open(context_path, "w") as f:
            json.dump(data, f, indent=2)

def validate_learning_path(modules: list) -> bool:
    """
    Validates learning path modules match required format and content standards
    """
    if not isinstance(modules, list) or not modules:
        return False

    required_fields = ['title', 'source', 'duration', 'link']
    return all(
        isinstance(module, dict) and 
        all(key in module for key in required_fields)
        for module in modules
    )

def validate_content(content: dict) -> bool:
    """
    Validates content matches required format and standards
    """
    if not isinstance(content, dict):
        return False

    required_fields = ['title', 'source', 'type', 'summary']
    return all(key in content for key in required_fields)