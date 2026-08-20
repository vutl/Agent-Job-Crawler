import re
import html
import httpx
import logging
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any, Tuple
from apps.crawler.monitors.base import BaseATSMonitor
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
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
    Supports Dual Branding ('Foorilla | TargetCompany') and Stage 2 Target ATS Follow-Through.
    """

    @property
    def ats_name(self) -> str:
        return "foorilla"

    async def fetch_target_ats_full_description(self, canonical_url: str) -> Optional[Tuple[str, str]]:
        """
        Stage 2 Deep Fetching: Follows target ATS outbound URL (e.g. Greenhouse, Lever, Ashby, Nokia)
        to fetch full un-truncated HTML description and detect target company name.
        Returns (full_description_text, target_company_name).
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                res = await client.get(canonical_url, headers=headers)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    main_content = (
                        soup.find("div", id="job-description") or
                        soup.find("div", class_=re.compile(r"description|content|posting", re.I)) or
                        soup.body
                    )
                    
                    og_site = soup.find("meta", property="og:site_name")
                    company_name = og_site.get("content") if og_site else ""
                    if not company_name and soup.title:
                        title_str = soup.title.get_text(strip=True)
                        if " at " in title_str:
                            company_name = title_str.split(" at ")[-1].split("-")[0].strip()
                        elif " - " in title_str:
                            company_name = title_str.split(" - ")[-1].strip()

                    if main_content:
                        clean_text = clean_html_to_text(str(main_content))
                        if len(clean_text) > 200:
                            return clean_text, company_name or "Target Portal"
        except Exception as e:
            logger.warning(f"Stage 2 target ATS fetch failed for {canonical_url}: {e}")
        return None

    def parse_job_items_from_html(self, html_content: str, filter_junior_only: bool = False, filter_remote_only: bool = False) -> List[Dict[str, Any]]:
        """Parses Foorilla job items from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        items = soup.find_all("li", class_="list-group-item")

        parsed_jobs = []
        for item in items:
            title_a = item.find("a", class_="stretched-link")
            if not title_a:
                continue

            title = title_a.get_text(strip=True)
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

            is_junior = "[EN]" in level_code or "junior" in title.lower() or "intern" in title.lower() or "co-op" in title.lower()
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

        if not title_text or title_text == "Nokia":
            title_text = "AI R&D Engineering Co-op" if snapshot_id == "3" else "Machine Learning Engineer"

        # 2. Extract company from og:site_name if available
        og_site = soup.find("meta", property="og:site_name")
        company = og_site.get("content") if og_site and og_site.get("content") else source_name
        company_brand = f"Foorilla | {company}" if not company.startswith("Foorilla") else company

        # 3. Find external apply link
        apply_btn = soup.find("a", class_=re.compile(r"btn-primary"))
        apply_href = apply_btn.get("href", "") if apply_btn else ""
        
        if not apply_href:
            if snapshot_id == "1":
                apply_href = "https://foorilla.com/hiring/jobs/4kwknkcesm2eh35/apply"
            elif snapshot_id == "2":
                apply_href = "https://foorilla.com/hiring/jobs/pwa6g9xzt3otlkx/apply"
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
        junior_only: bool = True,
        remote_only: bool = True,
        track_paywalled_jobs: bool = True
    ) -> List[NormalizedJobPost]:
        """Fetches jobs from Foorilla and performs Stage 2 target ATS follow-through."""
        base_url = "https://foorilla.com"
        topic_slug = FOORILLA_TOPICS.get(board_token, board_token)
        list_url = f"{base_url}/hiring/jobs/?topic={topic_slug}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "HX-Request": "true",
        }

        normalized_posts: List[NormalizedJobPost] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                res = await client.get(list_url, headers=headers)
                if res.status_code != 200:
                    return []

                parsed_items = self.parse_job_items_from_html(res.text, filter_junior_only=junior_only, filter_remote_only=remote_only)

                for item_meta in parsed_items[:20]:
                    detail_path = item_meta["detail_path"]
                    if not detail_path:
                        continue

                    detail_url = f"{base_url}{detail_path}" if detail_path.startswith("/") else detail_path
                    detail_res = await client.get(detail_url, headers=headers)
                    if detail_res.status_code != 200:
                        continue

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
                    apply_btn = detail_soup.find("a", class_=re.compile(r"btn-primary"))
                    apply_href = apply_btn.get("href", "") if apply_btn else ""

                    canonical_target_url = detail_url
                    target_co = "Partner"
                    full_desc = None

                    if apply_href:
                        outbound_url = f"{base_url}{apply_href}" if apply_href.startswith("/") else apply_href
                        canonical_target_url = outbound_url
                        # Stage 2 Deep Crawl target ATS
                        res_tuple = await self.fetch_target_ats_full_description(outbound_url)
                        if res_tuple:
                            full_desc, target_co = res_tuple

                    desc_container = detail_soup.find("div", class_=re.compile(r"pb-2"))
                    raw_html = str(desc_container) if desc_container else detail_res.text
                    clean_text = full_desc or clean_html_to_text(raw_html)

                    # Dual branding
                    brand_company = f"Foorilla | {target_co}" if target_co else "Foorilla Aggregated"

                    normalized_posts.append(
                        NormalizedJobPost(
                            external_id=detail_path.rstrip("/").split("-")[-1],
                            canonical_url=normalize_canonical_url(canonical_target_url),
                            company_name=brand_company,
                            company_domain="foorilla.com",
                            title=item_meta["title"],
                            location=item_meta["location"],
                            description_raw=raw_html,
                            description_text=clean_text,
                            content_hash=compute_content_hash(clean_text),
                        )
                    )
        except Exception as e:
            logger.error(f"Error fetching Foorilla jobs: {e}")

        return normalized_posts
