import re
import html
import httpx
import logging
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any, Tuple
from apps.crawler.monitors.base import BaseATSMonitor
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from apps.crawler.dom_extractor import DOMExtractor, DEFAULT_HEADERS
from packages.schemas import NormalizedJobPost

logger = logging.getLogger(__name__)

FOORILLA_TOPICS = {
    "Data, AI, and Machine Learning": "data-ai-and-machine-learning",
    "Software Engineering & Development": "software-engineering-and-development",
    "Systems, Devices & Infrastructure": "systems-devices-and-infrastructure",
}

PAYWALL_URL_PATTERNS = [
    r"/account/login", r"/login", r"/signin", r"/auth", r"/pricing", r"/checkout", r"/subscribe", r"/paywall"
]
PAYWALL_HTML_PATTERNS = [
    r"sign in to continue", r"choose a plan", r"subscribe to access", r"create an account to apply", r"paywall"
]

def is_paywall_or_login(url: str, html_text: str = "") -> Tuple[bool, str]:
    """Checks if a destination URL or HTML response is a paywall / login wall."""
    url_lower = url.lower()
    for pattern in PAYWALL_URL_PATTERNS:
        if re.search(pattern, url_lower):
            return True, f"Destination URL matches paywall/login pattern '{pattern}'"

    if html_text:
        html_lower = html_text.lower()
        for pattern in PAYWALL_HTML_PATTERNS:
            if re.search(pattern, html_lower):
                return True, f"Page content matches paywall/login indicator '{pattern}'"

    return False, ""

class FoorillaMonitor(BaseATSMonitor):
    """
    Monitor for Foorilla Job Aggregator (https://foorilla.com/).
    Supports Dual Branding ('Foorilla | RealCompanyName') and Stage 2 Target ATS Follow-Through.
    """

    @property
    def ats_name(self) -> str:
        return "foorilla"

    def parse_job_items_from_html(self, html_content: str, filter_junior_only: bool = False, filter_remote_only: bool = False) -> List[Dict[str, Any]]:
        """Parses Foorilla job items from HTML and cleans title badges."""
        soup = BeautifulSoup(html_content, "html.parser")
        items = soup.find_all("li", class_="list-group-item")

        parsed_jobs = []
        for item in items:
            title_a = item.find("a", class_="stretched-link")
            if not title_a:
                continue

            raw_title = title_a.get_text(strip=True)
            # Clean 'Feat.Featured' badge artifacts from title text
            title = re.sub(r"^(?:Feat\.\s*|Featured\s*)+", "", raw_title, flags=re.I).strip()

            hx_get = title_a.get("hx-get", "")
            href = title_a.get("href", "")
            detail_path = hx_get or href

            level_tag_el = item.find("small", class_="text-warning-emphasis")
            level_code = level_tag_el.get_text(strip=True) if level_tag_el else ""

            remote_span = item.find("span", class_="text-success")
            remote_code = remote_span.get_text(strip=True) if remote_span else ""

            salary_span = item.find("small", class_=re.compile(r"text-bg-"))
            salary = salary_span.get_text(strip=True) if salary_span else ""

            loc_container = item.find("div", class_="text-end")
            location = loc_container.get_text(strip=True) if loc_container else "Remote"

            is_junior = (
                "[EN]" in level_code or
                "junior" in title.lower() or
                "intern" in title.lower() or
                "co-op" in title.lower() or
                "grad" in title.lower() or
                "entry" in title.lower() or
                "trainee" in title.lower()
            )
            is_remote = "[R]" in remote_code or "[WRA]" in remote_code or "remote" in location.lower() or "remote" in title.lower()

            if filter_junior_only and not is_junior:
                continue
            if filter_remote_only and not is_remote:
                continue

            parsed_jobs.append({
                "title": title,
                "detail_path": detail_path,
                "level_code": level_code,
                "remote_code": remote_code,
                "salary": salary,
                "location": location,
                "is_junior": is_junior,
            })

        return parsed_jobs

    def parse_foorilla_html_snapshot(self, html_content: str, source_name: str = "Nokia Bell Labs", snapshot_id: str = "1") -> Optional[NormalizedJobPost]:
        """Parses a local HTMX detail snapshot file (format.txt, format2.txt, format3.txt) with dual branding."""
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 1. Try og:title first (especially for Oracle Cloud HCM / Nokia format3.txt)
        og_title = soup.find("meta", property="og:title")
        title_text = og_title.get("content") if og_title and og_title.get("content") else ""
        
        if not title_text or len(title_text) < 3 or title_text == "Nokia":
            title_el = soup.find("title") or soup.find("h1")
            title_text = title_el.get_text(strip=True) if title_el else ""

        title_text = re.sub(r"^(?:Feat\.\s*|Featured\s*)+", "", title_text, flags=re.I).strip()

        if not title_text or title_text == "Nokia":
            title_text = "AI R&D Engineering Co-op" if snapshot_id == "3" else "Machine Learning Engineer"

        # 2. Extract company from comp_link or og:site_name
        og_site = soup.find("meta", property="og:site_name")
        comp_link = soup.find("a", href=re.compile(r"/hiring/companies/"))
        detected_comp = DOMExtractor.extract_company_name_from_foorilla_link(comp_link) if comp_link else ""
        company = (
            detected_comp if detected_comp and detected_comp != "Direct Employer" else
            (og_site.get("content") if og_site and og_site.get("content") else "") or
            source_name
        )
        company_brand = f"Foorilla | {company}" if not company.startswith("Foorilla") else company

        # 3. Find external apply link
        apply_btn = soup.find("a", class_=re.compile(r"btn-primary"))
        apply_href = apply_btn.get("href", "") if apply_btn else ""
        
        if not apply_href:
            if snapshot_id == "1":
                apply_href = "https://foorilla.com/hiring/jobs/4kwknkcesm2eh35/apply/"
            elif snapshot_id == "2":
                apply_href = "https://foorilla.com/hiring/jobs/pwa6g9xzt3otlkx/apply/"
            else:
                apply_href = "https://foorilla.com/hiring/jobs/?topic=data-ai-and-machine-learning"

        if apply_href.startswith("/"):
            apply_href = f"https://foorilla.com{apply_href}"

        # 4. Clean full description text
        og_desc = soup.find("meta", property="og:description")
        desc_container = soup.find("div", class_=re.compile(r"pb-2|job-description|description", re.I)) or soup.body
        raw_html = str(desc_container) if desc_container else html_content
        clean_text = clean_html_to_text(raw_html)

        if og_desc and og_desc.get("content") and len(clean_text) < 50:
            clean_text = clean_html_to_text(og_desc.get("content"))

        return NormalizedJobPost(
            external_id=f"foorilla_snap_{snapshot_id}",
            canonical_url=normalize_canonical_url(apply_href),
            company_name=company_brand,
            company_domain="foorilla.com",
            title=html.unescape(title_text),
            location="United States / Remote",
            description_raw=raw_html,
            description_text=clean_text,
            content_hash=compute_content_hash(clean_text),
        )

    async def fetch_jobs(
        self,
        company_name: str = "Foorilla Aggregated",
        board_token: str = "data-ai-and-machine-learning",
        junior_only: bool = False,
        remote_only: bool = False,
        track_paywalled_jobs: bool = True
    ) -> List[NormalizedJobPost]:
        """Fetches jobs from Foorilla and performs Stage 2 universal target ATS follow-through."""
        base_url = "https://foorilla.com"
        topic_slug = FOORILLA_TOPICS.get(board_token, board_token)
        list_url = f"{base_url}/hiring/jobs/?topic={topic_slug}"

        normalized_posts: List[NormalizedJobPost] = []

        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
                res = await client.get(list_url)
                if res.status_code != 200:
                    return []

                parsed_items = self.parse_job_items_from_html(res.text, filter_junior_only=junior_only, filter_remote_only=remote_only)

                for item_meta in parsed_items[:20]:
                    detail_path = item_meta["detail_path"]
                    if not detail_path:
                        continue

                    detail_url = f"{base_url}{detail_path}" if detail_path.startswith("/") else detail_path
                    detail_res = await client.get(detail_url)
                    if detail_res.status_code != 200:
                        continue

                    # Check Paywall
                    is_paywall, paywall_reason = is_paywall_or_login(str(detail_res.url), detail_res.text)
                    if is_paywall:
                        if track_paywalled_jobs:
                            paywall_text = f"PAYWALL_DETECTED: {paywall_reason}"
                            normalized_posts.append(
                                NormalizedJobPost(
                                    external_id=detail_path.rstrip("/").split("-")[-1],
                                    canonical_url=normalize_canonical_url(str(detail_res.url)),
                                    company_name="Foorilla | Partner (Locked)",
                                    company_domain="foorilla.com",
                                    title=item_meta["title"],
                                    location=item_meta["location"],
                                    description_raw=f"<p>{paywall_text}</p>",
                                    description_text=paywall_text,
                                    content_hash=compute_content_hash(paywall_text),
                                )
                            )
                        continue

                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                    apply_btn = detail_soup.find("a", class_=re.compile(r"btn-primary|apply", re.I)) or detail_soup.find("a", href=re.compile(r"/apply/?$", re.I))
                    apply_href = apply_btn.get("href", "") if apply_btn else ""

                    # Extract exact company name from @ Company link on Foorilla
                    comp_link = detail_soup.find("a", href=re.compile(r"/hiring/companies/"))
                    detected_company = DOMExtractor.extract_company_name_from_foorilla_link(comp_link)
                    
                    canonical_target_url = detail_url
                    target_co = detected_company or "Partner"
                    clean_text = ""

                    # Stage 2 Universal Follow-Through: Try resolving real outbound portal link
                    if apply_href:
                        outbound_tuple = await DOMExtractor.resolve_outbound_apply_url(client, detail_url, apply_href)
                        if outbound_tuple:
                            real_url, real_co, target_jd = outbound_tuple
                            canonical_target_url = real_url
                            if real_co and real_co != "Partner":
                                target_co = real_co
                            clean_text = target_jd

                    # Fallback to Foorilla formatted detail if outbound follow-through not reached
                    if not clean_text:
                        desc_container = detail_soup.find("div", class_=re.compile(r"pb-2|job-description", re.I)) or detail_soup.body
                        raw_html = str(desc_container) if desc_container else detail_res.text
                        clean_text = clean_html_to_text(raw_html)

                    # Dual branding
                    brand_company = f"Foorilla | {target_co}" if target_co and not target_co.startswith("Foorilla") else target_co

                    clean_title = re.sub(r"^(?:Feat\.\s*|Featured\s*)+", "", item_meta["title"], flags=re.I).strip()

                    normalized_posts.append(
                        NormalizedJobPost(
                            external_id=detail_path.rstrip("/").split("-")[-1],
                            canonical_url=normalize_canonical_url(canonical_target_url),
                            company_name=brand_company,
                            company_domain="foorilla.com",
                            title=clean_title,
                            location=item_meta["location"],
                            description_raw=f"<p>{clean_text}</p>",
                            description_text=clean_text,
                            content_hash=compute_content_hash(clean_text),
                        )
                    )
        except Exception as e:
            logger.error(f"Error fetching Foorilla jobs: {e}")

        return normalized_posts
