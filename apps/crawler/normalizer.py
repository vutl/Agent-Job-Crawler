import hashlib
import html
import re
from bs4 import BeautifulSoup

def clean_html_to_text(html_content: str) -> str:
    """
    Converts raw HTML into clean, formatted structured text / Markdown.
    Preserves headings (###), bullet points (- ), and paragraph breaks (\n\n)
    while removing all unwanted tags, scripts, and decoding HTML entities.
    """
    if not html_content:
        return ""

    # 1. Unescape HTML entities first (&lt;div&gt; -> <div>, &nbsp; -> space)
    unescaped = html.unescape(html_content)
    unescaped = unescaped.replace("&nbsp;", " ").replace("&nbsp", " ")

    # 2. Parse with BeautifulSoup
    soup = BeautifulSoup(unescaped, "html.parser")

    # Remove script, style, noscript, svg, iframe elements
    for element in soup(["script", "style", "noscript", "svg", "iframe"]):
        element.decompose()

    # Replace headings with markdown style
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        h_text = h.get_text(strip=True)
        if h_text:
            h.replace_with(f"\n\n### {h_text}\n\n")

    # Replace list items with bullet points
    for li in soup.find_all("li"):
        li_text = li.get_text(strip=True)
        if li_text:
            li.replace_with(f"\n- {li_text}")

    # Replace paragraph and breaks with line breaks
    for p in soup.find_all(["p", "div", "section", "article"]):
        p.insert_before("\n\n")
        p.insert_after("\n\n")

    for br in soup.find_all("br"):
        br.replace_with("\n")

    # Get clean text
    raw_text = soup.get_text()

    # 3. Strip any residual unparsed HTML tag artifacts (e.g. <div class="...">)
    clean = re.sub(r"<[^>]+>", " ", raw_text)

    # 4. Clean Foorilla / Aggregator shorthand section patterns into rich Markdown
    clean = re.sub(r"Tasks:\s*\*", "\n\n### Tasks\n\n- ", clean, flags=re.I)
    clean = re.sub(r"Tasks:\s*", "\n\n### Tasks\n\n- ", clean, flags=re.I)
    clean = re.sub(r"Perks/Benefits:\s*\+?", "\n\n### Perks & Benefits\n\n- ", clean, flags=re.I)
    clean = re.sub(r"Skills/Tech stack required:\s*", "\n\n### Skills & Tech Stack Required\n\n", clean, flags=re.I)
    clean = re.sub(r"Educational requirements:\s*", "\n\n### Educational Requirements\n\n", clean, flags=re.I)
    clean = re.sub(r"Role\(s\):\s*", "\n\n### Role(s)\n\n", clean, flags=re.I)
    clean = re.sub(r"Where you will work", "\n\n### Where You Will Work\n\n", clean, flags=re.I)
    clean = re.sub(r"What you will do", "\n\n### What You Will Do\n\n", clean, flags=re.I)
    clean = re.sub(r"What you bring", "\n\n### What You Bring\n\n", clean, flags=re.I)
    clean = re.sub(r"What we offer", "\n\n### What We Offer\n\n", clean, flags=re.I)
    clean = re.sub(r"What we value", "\n\n### What We Value\n\n", clean, flags=re.I)

    # Clean double bullet markers (e.g. '• *', '• +', '- *')
    clean = re.sub(r"[\u2022\u25cf\u25cb]\s*[\*\+\-]?\s*", "\n- ", clean)
    clean = re.sub(r"\n\s*[\*\+]\s+", "\n- ", clean)

    # Remove boilerplate ingestion prefixes
    clean = re.sub(r"^Job Posting:\s*.*?\.\s*", "", clean, flags=re.I)

    # 5. Clean line by line
    lines = []
    for line in clean.splitlines():
        line_clean = re.sub(r"[ \t]+", " ", line).strip()
        # Clean stray bullet characters on line start
        line_clean = re.sub(r"^[\u2022\u25cf\u25cb]\s*", "- ", line_clean)
        line_clean = re.sub(r"^-\s*[\*\+]\s*", "- ", line_clean)
        
        if line_clean:
            lines.append(line_clean)
        elif lines and lines[-1] != "":
            lines.append("")

    # Join with clean line breaks
    formatted_text = "\n".join(lines).strip()
    return formatted_text

def compute_content_hash(text: str) -> str:
    """Computes SHA256 content hash of normalized job description text."""
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def normalize_canonical_url(url: str) -> str:
    """
    Strips tracking params and trailing slashes to form canonical URL.
    CRITICAL: Preserves exact character casing for case-sensitive ATS/Foorilla tokens!
    """
    if not url:
        return ""
    # Strip tracking query params and fragments
    clean_url = url.split("?")[0].split("#")[0].rstrip("/")
    return clean_url
