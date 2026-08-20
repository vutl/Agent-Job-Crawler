import re
from typing import Tuple

# Non-technical / corporate / business / field support title patterns (Case-insensitive)
NON_TECH_TITLE_PATTERNS = [
    r"\bvideo\s+editor\b",
    r"\bcontent\s+creator\b",
    r"\bcopywriter\b",
    r"\bgraphic\s+designer\b",
    r"\bsales\b",
    r"\baccountant\b|\baccounting\b|\btax\b|\bpayroll\b|\baudit\b",
    r"\bstatutory\b",
    r"\bhr\b|\brecruiter\b|\btalent\s+acquisition\b",
    r"\breceptionist\b|\boffice\s+manager\b",
    r"\blegal\b|\bcounsel\b|\bcompliance\b",
    r"\bcustomer\s+(?:engineer|service|success|support|operations|experience)\b",
    r"\bsolutions\s+(?:engineer|architect|consultant|specialist)\b",
    r"\bsales\s+(?:engineer|executive|representative|manager|director)\b",
    r"\baccount\s+(?:executive|manager|engineer)\b",
    r"\btechnical\s+account\s+manager\b",
    r"\bpartner\s+(?:engineer|manager|director)\b",
    r"\bstrategic\s+partner\b",
    r"\bscm\b|\bsupply\s+chain\b",
    r"\boperations\s+(?:lead|manager|director|specialist)\b",
    r"\bpayment\s+operations\b",
    r"\bfinancial\s+systems\b",
    r"\bonline\s+data\s+analyst\b",
    r"\bdata\s+annotator\b",
    r"\bsocial\s+media\b",
    r"\bmarketing\s+specialist\b|\bmarketing\s+manager\b",
    r"\bproduct\s+marketing\b",
    r"\bproduct\s+manager\b(?!.*(?:ai|ml|machine\s+learning))",
    r"\bexecutive\s+assistant\b",
]

# Essential technical / engineering keywords
TECH_KEYWORDS = [
    "python", "java", "c++", "golang", "rust", "sql", "pytorch", "tensorflow", "keras",
    "scikit-learn", "pandas", "numpy", "docker", "kubernetes", "aws", "gcp", "azure",
    "fastapi", "flask", "django", "spark", "hadoop", "airflow", "dbt", "kafka",
    "machine learning", "deep learning", "ai", "ml", "ml engineer", "data engineer",
    "data scientist", "platform engineer", "mlops", "llm", "rag", "vector search",
    "langchain", "llamaindex", "transformers", "huggingface", "cuda",
    "software", "developer", "engineer", "backend", "frontend", "fullstack",
    "react", "typescript", "javascript", "c#", ".net", "systems", "intern", "internship"
]

# Tech role indicators
TECH_ROLE_PATTERNS = [
    r"\b(?:ai|ml|machine\s+learning|deep\s+learning|nlp|computer\s+vision|data|data\s+science|data\s+engineer|data\s+platform|mlops|software|backend|frontend|fullstack|infrastructure|systems|platform|security|distributed|cloud|devops|site\s+reliability|sre|research\s+scientist|algorithm)\s*(?:engineer|developer|scientist|specialist|architect|lead|manager|researcher|intern)?\b"
]

def is_prefilter_pass(title: str, description_text: str) -> Tuple[bool, str]:
    """
    Fast heuristic pre-filter running in <1ms at 0 token cost.
    Returns (should_call_llm: bool, reason: str).
    """
    title_lower = title.lower()
    desc_lower = description_text.lower()

    # Rule 1: Instant rejection for non-technical / business / corporate titles
    for pattern in NON_TECH_TITLE_PATTERNS:
        if re.search(pattern, title_lower):
            return False, f"Rejected by pre-filter: Title '{title}' matches non-technical pattern '{pattern}'"

    # Rule 2: Minimum technical keyword or tech role check
    has_tech_keyword = (
        any(kw in desc_lower or kw in title_lower for kw in TECH_KEYWORDS) or
        any(re.search(pat, title_lower) for pat in TECH_ROLE_PATTERNS)
    )
    if not has_tech_keyword:
        return False, "Rejected by pre-filter: Zero technical keywords found in job description"

    # Passed pre-filter -> safe to send to LLM
    return True, "Passed heuristic pre-filter"

