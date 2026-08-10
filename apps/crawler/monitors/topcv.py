from __future__ import annotations

import json
import logging
import re
import unicodedata
from typing import List, Optional, Tuple
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup

from packages.schemas import NormalizedJobPost
from .base import BaseATSMonitor
from ..normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

class TopCVMonitor(BaseATSMonitor):
    """Monitor & Crawler for TopCV.vn job portal."""

    EXPERIENCE_PARAM_MAP = {
        None: "",
        "": "",
        "all": "",
        0: "",
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
    }

    @property
    def ats_name(self) -> str:
        return "topcv"

    @staticmethod
    def slugify(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value or "")
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
        return slug or "viec-lam"

    @classmethod
    def build_search_url(cls, keyword: str, location: str = "Hà Nội", experience: str = "") -> str:
        keyword_slug = cls.slugify(keyword)
        location_slug = cls.slugify(location)
        base_url = f"https://www.topcv.vn/tim-viec-lam-{keyword_slug}-tai-{location_slug}-kl1"
        exp_value = cls.EXPERIENCE_PARAM_MAP.get(experience, "")
        if not exp_value:
            return base_url
        return f"{base_url}?exp={quote_plus(exp_value)}"

    @staticmethod
    def _extract_job_id(url: str) -> str:
        match = re.search(r"/(\d+)\.html", url)
        return match.group(1) if match else ""

    @staticmethod
    def _strip_tracking(url: str) -> str:
        return url.split("?", 1)[0].split("#", 1)[0]

    def parse_search_jobs(
        self,
        html: str,
        query: str,
        max_jobs: int = 20,
    ) -> List[dict]:
        """Parses job cards from TopCV search result HTML page."""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select("div.job-item-search-result")

        out: List[dict] = []
        seen_urls = set()

        for card in cards:
            link = card.select_one('h3.title a[href*="/viec-lam/"]')
            if not link:
                continue

            raw_url = (link.get("href") or "").strip()
            if not raw_url:
                continue

            url = self._strip_tracking(raw_url)
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title = clean_html_to_text(link.get_text(" ", strip=True))
            company_el = card.select_one(".company-name") or link
            company = clean_html_to_text(company_el.get_text(" ", strip=True))

            location_el = card.select_one("label.address .city-text") or card.select_one("label.address")
            location = clean_html_to_text(location_el.get_text(" ", strip=True)) if location_el else None

            job_id = card.get("data-job-id") or self._extract_job_id(url)

            out.append({
                "external_id": str(job_id),
                "url": url,
                "title": title,
                "company": company,
                "location": location,
            })

            if len(out) >= max_jobs:
                break

        return out

    def parse_job_detail(self, html: str, fallback_title: str = "", fallback_company: str = "") -> Tuple[dict, str]:
        """
        Parses TopCV detail HTML using JSON-LD first with DOM fallback.
        Returns a tuple of (parsed_metadata dict, raw_description_html/text).
        """
        soup = BeautifulSoup(html, "html.parser")

        title = fallback_title
        company = fallback_company
        location = None
        desc_raw_parts = []
        desc_text_parts = []

        # 1. Try JSON-LD parsing
        json_ld_data = {}
        for script in soup.select('script[type="application/ld+json"]'):
            raw_ld = script.string or script.get_text(strip=True)
            if not raw_ld:
                continue
            try:
                payload = json.loads(raw_ld)
                if isinstance(payload, dict) and payload.get("@type") == "JobPosting":
                    json_ld_data = payload
                    break
                elif isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and item.get("@type") == "JobPosting":
                            json_ld_data = item
                            break
            except json.JSONDecodeError:
                pass

        if json_ld_data:
            if json_ld_data.get("title"):
                title = str(json_ld_data["title"]).strip()
            hiring_org = json_ld_data.get("hiringOrganization") or {}
            if isinstance(hiring_org, dict) and hiring_org.get("name"):
                company = str(hiring_org["name"]).strip()
            if json_ld_data.get("description"):
                desc_raw_parts.append(str(json_ld_data["description"]))
                desc_text_parts.append(clean_html_to_text(str(json_ld_data["description"])))

        # 2. DOM fallback for title & company
        if not title:
            title_el = soup.select_one("h1.job-detail__info--title")
            if title_el:
                title = clean_html_to_text(title_el.get_text(" ", strip=True))

        if not company:
            company_el = soup.select_one(".job-detail__company .company-content__title--label")
            if company_el:
                company = clean_html_to_text(company_el.get_text(" ", strip=True))

        # 3. DOM fallback for job description blocks
        for block in soup.select("div.job-description__item"):
            heading_el = block.select_one("h3")
            content_el = block.select_one(".job-description__item--content")
            if heading_el and content_el:
                heading = clean_html_to_text(heading_el.get_text(" ", strip=True))
                content_html = str(content_el)
                content_text = clean_html_to_text(content_html)
                desc_raw_parts.append(f"<h3>{heading}</h3>\n{content_html}")
                desc_text_parts.append(f"{heading}:\n{content_text}")

        # Location fallback
        loc_el = soup.select_one(".job-detail__info--section-content-value")
        if loc_el:
            location = clean_html_to_text(loc_el.get_text(" ", strip=True))

        full_raw = "\n".join(desc_raw_parts) if desc_raw_parts else f"<h1>{title}</h1>"
        full_text = "\n\n".join(desc_text_parts) if desc_text_parts else title

        meta = {
            "title": title or "Untitled",
            "company": company or "TopCV Employer",
            "location": location,
        }
        return meta, full_raw, full_text

    async def fetch_jobs_by_keyword(
        self,
        keyword: str,
        location: str = "Hà Nội",
        experience: str = "",
        max_jobs: int = 10,
    ) -> List[NormalizedJobPost]:
        """Crawls TopCV for a given search keyword and returns NormalizedJobPost objects."""
        search_url = self.build_search_url(keyword, location, experience)
        posts: List[NormalizedJobPost] = []

        async with httpx.AsyncClient(timeout=20.0, headers=DEFAULT_HEADERS, follow_redirects=True) as client:
            try:
                res = await client.get(search_url)
                res.raise_for_status()
                search_html = res.text
            except Exception as e:
                logger.error(f"Failed to fetch TopCV search URL {search_url}: {e}")
                return posts

            cards = self.parse_search_jobs(search_html, query=keyword, max_jobs=max_jobs)

            for card in cards:
                try:
                    detail_res = await client.get(card["url"])
                    if detail_res.status_code != 200:
                        continue
                    detail_html = detail_res.text
                    meta, desc_raw, desc_text = self.parse_job_detail(
                        detail_html,
                        fallback_title=card["title"],
                        fallback_company=card["company"],
                    )

                    content_hash = compute_content_hash(desc_text)
                    canonical_url = normalize_canonical_url(card["url"])

                    post = NormalizedJobPost(
                        external_id=card["external_id"],
                        canonical_url=canonical_url,
                        company_name=meta["company"],
                        company_domain="topcv.vn",
                        title=meta["title"],
                        location=meta["location"] or card["location"],
                        description_raw=desc_raw,
                        description_text=desc_text,
                        content_hash=content_hash,
                    )
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Error fetching TopCV job detail {card['url']}: {e}")

        return posts

    async def fetch_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        """BaseATSMonitor interface implementation using board_token as keyword."""
        return await self.fetch_jobs_by_keyword(keyword=board_token, max_jobs=10)
