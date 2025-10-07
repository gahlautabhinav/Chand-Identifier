# scripts/utils.py
import unicodedata
import re

# Characters we want to preserve explicitly (so don't strip them)
PRESERVE = {
    'ऽ',  # avagraha
    '\u0902',  # anusvara ं
    '\u0903',  # visarga ः
    '\u0901',  # chandrabindu ँ
    '\u0950',  # OM ॐ
    '\u094D'   # virama ् (keep conjunct info)
}

# Regex: punctuation to remove/replace (keep devanagari diacritics above).
# We will replace danda characters with spaces to preserve pada boundaries.
_DANDA_RE = re.compile(r'[॥।]+')
_PUNCT_RE = re.compile(r'[\u2000-\u206F\u2E00-\u2E7F\.,;:"\?\!\(\)\[\]\{\}—\-–/\\\|<>@#\$%\^&\*\+=_`~]')

def normalize_text(text: str) -> str:
    """
    Normalize text for pipeline processing.

    - Unicode NFC normalize
    - Replace dandas (।, ॥) with spaces
    - Keep devanagari combining marks and special signs (anusvara, visarga, avagraha, virama, OM)
    - Replace other punctuation with space
    - Ensure 'ॐ' is separated as a token (surrounded by spaces)
    - Collapse multiple whitespace to a single space and strip ends
    """
    if text is None:
        return ""
    # unicode NFC
    text = unicodedata.normalize('NFC', text)

    # Replace common danda characters with space (preserve pada boundaries)
    text = _DANDA_RE.sub(' ', text)

    # Ensure OM (ॐ) is spaced so syllabifier treats it as token
    # Use \u0950 for OM
    text = re.sub(r'\u0950', ' \u0950 ', text)

    # Replace common punctuation (ASCII + symbol ranges) with space
    text = _PUNCT_RE.sub(' ', text)

    # Remove stray ASCII control chars
    text = ''.join(ch for ch in text if ord(ch) >= 32)

    # Collapse multiple spaces/newlines/tabs to single space
    text = re.sub(r'\s+', ' ', text)

    # Trim
    text = text.strip()

    return text

