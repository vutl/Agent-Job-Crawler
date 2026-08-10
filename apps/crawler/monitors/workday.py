import httpx
import logging
from typing import List, Dict, Any, Optional
from apps.crawler.monitors.base import BaseATSMonitor
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from packages.schemas import NormalizedJobPost

logger = logging.getLogger(__name__)

class WorkdayMonitor(BaseATSMonitor):
    """Monitor for Workday ATS portals (*.myworkdayjobs.com)."""

    @property
    def ats_name(self) -> str:
        return "workday"

    async def fetch_jobs(self, company_name: str, board_token: str) -> List[NormalizedJobPost]:
        """
        board_token format: '{tenant}/{site}' or '{tenant}'
        Example: 'DataRobot_External_Careers' or 'datarobot/DataRobot_External_Careers'
        """
        parts = board_token.strip("/").split("/")
        if len(parts) == 2:
            tenant, site = parts[0], parts[1]
        else:
            tenant = company_name.lower().replace(" ", "").replace("-", "")
            site = parts[0]

        list_url = f"https://{tenant}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        normalized_posts: List[NormalizedJobPost] = []

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                res = await client.post(list_url, json=payload, headers=headers)
                if res.status_code != 200:
                    logger.warning(f"Workday API returned status {res.status_code} for {list_url}")
                    return []

                data = res.json()
                job_postings = data.get("jobPostings", [])

                for item in job_postings:
                    external_path = item.get("externalPath", "")
                    title = item.get("title", "")
                    location = item.get("location", "")

                    if not external_path.startswith("/"):
                        external_path = f"/{external_path}"

                    detail_url = f"https://{tenant}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/{site}{external_path}"
                    canonical_url = f"https://{tenant}.wd1.myworkdayjobs.com/en-US/{site}{external_path}"

                    detail_res = await client.get(detail_url, headers=headers)
                    if detail_res.status_code != 200:
                        continue

                    detail_json = detail_res.json()
                    detail_data = detail_json.get("jobPostingInfo", detail_json)
                    raw_html = detail_data.get("jobDescription", "")
                    clean_text = clean_html_to_text(raw_html)

                    if not clean_text:
                        continue

                    content_hash = compute_content_hash(clean_text)

                    normalized_posts.append(
                        NormalizedJobPost(
                            external_id=external_path.split("_")[-1] if "_" in external_path else external_path,
                            canonical_url=normalize_canonical_url(canonical_url),
                            company_name=company_name,
                            company_domain=f"{tenant}.myworkdayjobs.com",
                            title=title,
                            location=location or detail_data.get("location"),
                            description_raw=raw_html,
                            description_text=clean_text,
                            content_hash=content_hash,
                        )
                    )
        except Exception as e:
            logger.error(f"Error fetching Workday jobs for {board_token}: {e}")

        return normalized_posts
