import logging
from typing import List
import httpx
from packages.schemas import NormalizedJobPost
from .base import BaseATSMonitor
from ..normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url

logger = logging.getLogger(__name__)

class GreenhouseMonitor(BaseATSMonitor):
    @property
    def ats_name(self) -> str:
        return "greenhouse"

    async def fetch_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
        jobs: List[NormalizedJobPost] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch Greenhouse jobs for {board_token}: {e}")
                return jobs

        for item in data.get("jobs", []):
            raw_html = item.get("content", "")
            plain_text = clean_html_to_text(raw_html)
            content_hash = compute_content_hash(plain_text)
            canonical_url = normalize_canonical_url(item.get("absolute_url", ""))
            location_name = item.get("location", {}).get("name") if isinstance(item.get("location"), dict) else None

            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=canonical_url,
                company_name=company_name,
                company_domain=f"{board_token}.com",
                title=item.get("title", "Untitled"),
                location=location_name,
                description_raw=raw_html,
                description_text=plain_text,
                content_hash=content_hash,
            )
            jobs.append(post)

        return jobs
