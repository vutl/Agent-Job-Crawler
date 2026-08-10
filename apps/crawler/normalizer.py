import hashlib
import html
import re
from bs4 import BeautifulSoup

def clean_html_to_text(html_content: str) -> str:
    """Converts raw HTML (including entity-encoded HTML) into clean plain text for hash computation and UI display."""
    if not html_content:
        return ""

    # 1. Unescape HTML entities first (&lt;div&gt; -> <div>)
    unescaped = html.unescape(html_content)

    # 2. Parse with BeautifulSoup
    soup = BeautifulSoup(unescaped, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    text = soup.get_text(separator=" ")

    # 3. Strip any residual unparsed HTML tag artifacts (e.g. <div class="...">)
    text = re.sub(r"<[^>]+>", " ", text)

    # 4. Remove boilerplate ingestion prefixes
    text = re.sub(r"^Job Posting:\s*.*?\.\s*", "", text, flags=re.I)
    text = re.sub(r"^Tasks:\s*", "", text, flags=re.I)

    # 5. Clean up multiple spaces and empty lines
    cleaned_text = re.sub(r"\s+", " ", text).strip()
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
