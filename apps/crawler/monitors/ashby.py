import logging
from typing import List, Dict, Any, Optional
import httpx

from packages.schemas import NormalizedJobPost
from ..normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url

logger = logging.getLogger(__name__)

ASHBY_COMPANIES = [
    ("Cohere", "cohere"),
    ("Perplexity AI", "perplexity"),
    ("ElevenLabs", "elevenlabs"),
    ("Linear", "linear"),
    ("Baseten", "baseten"),
    ("Modal", "modal"),
    ("Suno", "suno"),
]

class AshbyMonitor:
    """Crawler monitor for AshbyHQ public job boards."""

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    async def fetch_company_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        """Fetches all active jobs for a company from AshbyHQ posting API."""
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board_token}"
        posts: List[NormalizedJobPost] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                res = await client.get(url)
                if res.status_code != 200:
                    logger.warning(f"Ashby API error {res.status_code} for {company_name} ({board_token})")
                    return []

                data = res.json()
                jobs = data.get("jobs", [])
                logger.info(f"Ashby [{company_name}]: Retrieved {len(jobs)} live postings.")

                for j in jobs:
                    title = j.get("title", "Software Engineer")
                    jid = str(j.get("id", ""))
                    apply_url = j.get("jobUrl") or f"https://jobs.ashbyhq.com/{board_token}/{jid}"
                    canonical_url = normalize_canonical_url(apply_url)

                    is_remote = j.get("isRemote") is True
                    raw_loc = (j.get("location") or "Remote").strip()

                    if is_remote and "remote" not in raw_loc.lower():
                        location = f"{raw_loc} (Remote)"
                    elif is_remote:
                        location = raw_loc or "Remote"
                    else:
                        location = raw_loc or "Distributed"

                    desc_plain = j.get("descriptionPlain") or ""
                    desc_html = j.get("descriptionHtml") or ""
                    clean_text = clean_html_to_text(desc_html) if desc_html else (desc_plain or f"{title} at {company_name}")
                    content_hash = compute_content_hash(clean_text)

                    posts.append(
                        NormalizedJobPost(
                            external_id=f"ashby-{board_token}-{jid}",
                            canonical_url=canonical_url,
                            company_name=company_name,
                            title=title,
                            location=location,
                            description_raw=desc_html or clean_text,
                            description_text=clean_text,
                            content_hash=content_hash,
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to fetch Ashby jobs for {company_name}: {e}")

        return posts

    async def fetch_all_frontier_boards(self) -> List[NormalizedJobPost]:
        """Fetches jobs across all configured Ashby AI companies."""
        all_posts: List[NormalizedJobPost] = []
        for cname, token in ASHBY_COMPANIES:
            posts = await self.fetch_company_jobs(cname, token)
            all_posts.extend(posts)
        return all_posts
