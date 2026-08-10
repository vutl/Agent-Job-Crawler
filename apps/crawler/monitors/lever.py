import logging
from typing import List
import httpx
from packages.schemas import NormalizedJobPost
from .base import BaseATSMonitor
from ..normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url

logger = logging.getLogger(__name__)

class LeverMonitor(BaseATSMonitor):
    @property
    def ats_name(self) -> str:
        return "lever"

    async def fetch_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        url = f"https://api.lever.co/v0/postings/{board_token}?mode=json"
        jobs: List[NormalizedJobPost] = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                logger.error(f"Failed to fetch Lever jobs for {board_token}: {e}")
                return jobs

        for item in data:
            # Lever puts raw description HTML in "description" plus "lists"
            desc_raw = item.get("description", "")
            for lst in item.get("lists", []):
                title = lst.get("text", "")
                content = lst.get("content", "")
                desc_raw += f"\n<h3>{title}</h3>\n{content}"

            plain_text = clean_html_to_text(desc_raw)
            content_hash = compute_content_hash(plain_text)
            canonical_url = normalize_canonical_url(item.get("hostedUrl", ""))
            location_name = item.get("categories", {}).get("location") if isinstance(item.get("categories"), dict) else None

            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=canonical_url,
                company_name=company_name,
                company_domain=f"{board_token}.com",
                title=item.get("text", "Untitled"),
                location=location_name,
                description_raw=desc_raw,
                description_text=plain_text,
                content_hash=content_hash,
            )
            jobs.append(post)

        return jobs
