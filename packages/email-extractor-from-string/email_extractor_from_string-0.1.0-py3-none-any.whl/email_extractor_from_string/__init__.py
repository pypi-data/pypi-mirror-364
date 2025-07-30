import re
from typing import List, Optional

def extract_emails(text: str) -> Optional[List[str]]:
    """
    Extracts all email addresses from the input text.
    Returns a list of emails or None if none are found.
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails if emails else None
