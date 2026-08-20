import re
import json
import httpx
import logging
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from apps.crawler.monitors.base import BaseATSMonitor
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from packages.schemas import NormalizedJobPost

logger = logging.getLogger(__name__)

class JobrightMonitor(BaseATSMonitor):
    """
    Monitor for Jobright.ai AI Job Search Aggregator (https://jobright.ai/).
    Supports 2-Stage Deep Crawling:
    - Stage 1: Listing Discovery & JSON-LD extraction
    - Stage 2: Outbound Target ATS Follow-Through (Fetching full JD directly from Greenhouse/Lever/Ashby)
    """

    @property
    def ats_name(self) -> str:
        return "jobright"

    async def fetch_target_ats_full_description(self, canonical_url: str) -> Optional[str]:
        """
        Stage 2 Deep Crawling: Follows the target outbound ATS link (e.g. Ashby, Greenhouse, Lever)
        to fetch the full, un-truncated official job description HTML.
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
                    # Try common ATS description containers
                    main_content = (
                        soup.find("div", id="job-description") or
                        soup.find("div", class_=re.compile(r"description|content|posting", re.I)) or
                        soup.body
                    )
                    if main_content:
                        clean_text = clean_html_to_text(str(main_content))
                        if len(clean_text) > 300:
                            return clean_text
        except Exception as e:
            logger.warning(f"Stage 2 follow-through fetch failed for {canonical_url}: {e}")
        return None

    def parse_jobright_detail_html(self, html_content: str, fallback_source: str = "Jobright Aggregated") -> Optional[NormalizedJobPost]:
        """
        Parses a Jobright detail panel/modal HTML snapshot.
        Extracts structured JSON payload from script#jobright-helper-job-detail-info and script#job-posting (JSON-LD).
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Try script#jobright-helper-job-detail-info
        helper_script = soup.find("script", id="jobright-helper-job-detail-info")
        helper_data = {}
        if helper_script and helper_script.string:
            try:
                helper_data = json.loads(helper_script.string).get("jobResult", {})
            except Exception as e:
                logger.warning(f"Error parsing jobright-helper-job-detail-info: {e}")

        # 2. Try script#job-posting (Schema.org JSON-LD)
        ld_script = soup.find("script", id="job-posting")
        ld_data = {}
        if ld_script and ld_script.string:
            try:
                ld_data = json.loads(ld_script.string)
            except Exception as e:
                logger.warning(f"Error parsing job-posting JSON-LD: {e}")

        title = (
            helper_data.get("jobTitle") or
            ld_data.get("title") or
            (soup.title.string.split("@")[0].strip() if soup.title else "Untitled Job")
        )

        company_res = helper_data.get("companyResult", {})
        hiring_org = ld_data.get("hiringOrganization", {})
        company_name = (
            company_res.get("companyName") or
            hiring_org.get("name") or
            fallback_source
        )

        apply_url = (
            helper_data.get("originalUrl") or
            helper_data.get("applyLink") or
            ld_data.get("sameAs") or
            (soup.find("link", rel="canonical").get("href") if soup.find("link", rel="canonical") else "https://jobright.ai/jobs")
        )

        desc_raw = ld_data.get("description", "")
        if not desc_raw:
            responsibilities = helper_data.get("coreResponsibilities", [])
            skills_summaries = helper_data.get("skillSummaries", [])
            desc_raw = f"<p>{helper_data.get('jobSummary', '')}</p><ul>"
            for r in responsibilities:
                desc_raw += f"<li>{r}</li>"
            for s in skills_summaries:
                desc_raw += f"<li>{s}</li>"
            desc_raw += "</ul>"

        clean_text = clean_html_to_text(desc_raw)
        if not clean_text or len(clean_text) < 20:
            clean_text = f"{title} at {company_name}. Location: {helper_data.get('jobLocation', 'Remote')}"

        content_hash = compute_content_hash(clean_text)
        external_id = helper_data.get("jobId") or ld_data.get("identifier", {}).get("value") or "jobright_detail"

        return NormalizedJobPost(
            external_id=str(external_id),
            canonical_url=normalize_canonical_url(apply_url),
            company_name=company_name,
            company_domain="jobright.ai",
            title=title,
            location=helper_data.get("jobLocation") or "Remote",
            description_raw=desc_raw,
            description_text=clean_text,
            content_hash=content_hash,
        )

    def parse_jobright_html_snapshot(self, html_content: str, source_name: str = "Jobright Aggregated") -> List[NormalizedJobPost]:
        """
        Parses a Jobright HTML snapshot file (e.g. format_jobright.txt).
        Supports both detail panel snapshots and listing grid snapshots.
        """
        if "jobright-helper-job-detail-info" in html_content or "job-posting" in html_content:
            detail_post = self.parse_jobright_detail_html(html_content, fallback_source=source_name)
            if detail_post:
                return [detail_post]

        soup = BeautifulSoup(html_content, "html.parser")
        h2_titles = soup.find_all("h2", class_=re.compile(r"index_job-title"))

        normalized_posts: List[NormalizedJobPost] = []

        for idx, h2 in enumerate(h2_titles, 1):
            title = h2.get_text(strip=True)
            if not title:
                continue

            card = h2.find_parent("div", class_=re.compile(r"index_job-card|card|item")) or h2.parent.parent.parent

            comp_el = card.find(class_=re.compile(r"company|employer|brand", re.I)) if card else None
            company_text = comp_el.get_text(strip=True) if comp_el else ""
            company_name = company_text if company_text else "Jobright Aggregated"

            loc_el = card.find(class_=re.compile(r"location|city|place", re.I)) if card else None
            location = loc_el.get_text(strip=True) if loc_el else "Remote"

            link_el = card.find("a", href=True) if card else None
            href = link_el.get("href") if link_el else f"/jobs/jobright-{idx}"
            canonical_url = f"https://jobright.ai{href}" if href.startswith("/") else href

            desc_el = card.find(class_=re.compile(r"description|summary|detail|content", re.I)) if card else None
            raw_html = str(desc_el) if desc_el else str(card)
            clean_text = clean_html_to_text(raw_html)

            if not clean_text or len(clean_text) < 10:
                clean_text = f"Job Posting: {title} at {company_name}. Location: {location}."

            content_hash = compute_content_hash(clean_text)

            normalized_posts.append(
                NormalizedJobPost(
                    external_id=str(idx),
                    canonical_url=normalize_canonical_url(canonical_url),
                    company_name=company_name,
                    company_domain="jobright.ai",
                    title=title,
                    location=location,
                    description_raw=raw_html,
                    description_text=clean_text,
                    content_hash=content_hash,
                )
            )

        return normalized_posts

    async def fetch_jobs(self, company_name: str = "Jobright", board_token: str = "recommend") -> List[NormalizedJobPost]:
        """Fetches jobs from Jobright.ai."""
        url = f"https://jobright.ai/jobs/{board_token}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    posts = self.parse_jobright_html_snapshot(res.text, source_name=company_name)
                    # Stage 2 Deep Crawl: If description is short, attempt target ATS follow-through
                    for post in posts:
                        if len(post.description_text) < 300 and "jobright.ai" not in post.canonical_url:
                            full_desc = await self.fetch_target_ats_full_description(post.canonical_url)
                            if full_desc:
                                post.description_text = full_desc
                                post.description_raw = f"<p>{full_desc}</p>"
                                post.content_hash = compute_content_hash(full_desc)
                    return posts
        except Exception as e:
            logger.error(f"Error fetching Jobright jobs: {e}")

        return []
