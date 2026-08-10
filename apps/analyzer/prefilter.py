import re
from typing import Tuple

# Non-technical / irrelevant job title patterns (Case-insensitive)
NON_TECH_TITLE_PATTERNS = [
    r"\bvideo\s+editor\b",
    r"\bcontent\s+creator\b",
    r"\bcopywriter\b",
    r"\bgraphic\s+designer\b",
    r"\bsales\b",
    r"\baccountant\b",
    r"\bhr\b|\brecruiter\b",
    r"\breceptionist\b",
    r"\blegal\b",
    r"\bcustomer\s+service\b",
    r"\bsocial\s+media\b",
    r"\bmarketing\s+specialist\b",
    r"\bproduct\s+marketing\b",
    r"\bexecutive\s+assistant\b",
]

# Essential technical / engineering keywords
TECH_KEYWORDS = [
    "python", "java", "c++", "golang", "rust", "sql", "pytorch", "tensorflow", "keras",
    "scikit-learn", "pandas", "numpy", "docker", "kubernetes", "aws", "gcp", "azure",
    "fastapi", "flask", "django", "spark", "hadoop", "airflow", "dbt", "kafka",
    "machine learning", "deep learning", "ai", "ml", "data engineer", "software engineer",
    "backend", "frontend", "fullstack", "platform engineer", "mlops", "llm", "rag",
    "vector search", "langchain", "llamaindex", "transformers", "huggingface", "cuda"
]

def is_prefilter_pass(title: str, description_text: str) -> Tuple[bool, str]:
    """
    Fast heuristic pre-filter running in <1ms at 0 token cost.
    Returns (should_call_llm: bool, reason: str).
    """
    title_lower = title.lower()
    desc_lower = description_text.lower()

    # Rule 1: Instant rejection for non-technical titles
    for pattern in NON_TECH_TITLE_PATTERNS:
        if re.search(pattern, title_lower):
            return False, f"Rejected by pre-filter: Title matches non-technical pattern '{pattern}'"

    # Rule 2: Minimum technical keyword check in description
    has_tech_keyword = any(kw in desc_lower or kw in title_lower for kw in TECH_KEYWORDS)
    if not has_tech_keyword:
        return False, "Rejected by pre-filter: Zero technical keywords found in job description"

    # Passed pre-filter -> safe to send to LLM
    return True, "Passed heuristic pre-filter"
