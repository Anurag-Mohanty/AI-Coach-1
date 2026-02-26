"""
Central lookup so orchestrators can call tools by short names.
For now we only have the résumé extractor.  We'll add more entries
as we refactor other tools.
"""

from tools.resume.resume_agent import analyze_resume
from tools.linkedin.linkedin_agent import analyze_linkedin_profile

REGISTRY = {
    "resume_extract": analyze_resume,
    "linkedin_extract": analyze_linkedin_profile,
    # we'll add more tools later
}