import hashlib
import html
import re
from bs4 import BeautifulSoup, NavigableString, Tag

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

    # 4. Remove boilerplate ingestion prefixes
    clean = re.sub(r"^Job Posting:\s*.*?\.\s*", "", clean, flags=re.I)
    clean = re.sub(r"^Tasks:\s*", "", clean, flags=re.I)

    # 5. Clean line by line
    lines = []
    for line in clean.splitlines():
        line_clean = re.sub(r"[ \t]+", " ", line).strip()
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
    """Strips tracking params and trailing slashes to form canonical URL."""
    if not url:
        return ""
    url = url.split("?")[0].split("#")[0].rstrip("/")
    return url.lower()
