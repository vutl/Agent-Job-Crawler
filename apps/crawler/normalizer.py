import hashlib
import re
from bs4 import BeautifulSoup

def clean_html_to_text(html_content: str) -> str:
    """Converts raw HTML into clean plain text for hash computation and AI extraction."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text(separator="\n")
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
    return cleaned_text

def compute_content_hash(text: str) -> str:
    """Computes SHA256 content hash of normalized job description text."""
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def normalize_canonical_url(url: str) -> str:
    """Strips tracking params and trailing slashes to form canonical URL."""
    if not url:
        return ""
    url = url.split("?")[0].split("#")[0].rstrip("/")
    return url.lower()
