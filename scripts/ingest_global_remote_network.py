import asyncio
import httpx
import re
import os
import sys
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import SessionLocal, Job, Company
from packages.schemas import NormalizedJobPost
from apps.crawler.normalizer import clean_html_to_text, normalize_canonical_url, compute_content_hash
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("global_remote_network")

GREENHOUSE_BOARDS = [
    ("Cloudflare", "cloudflare"),
    ("Scale AI", "scaleai"),
    ("Figma", "figma"),
    ("Stripe", "stripe"),
    ("DataRobot", "datarobot"),
]

async def fetch_greenhouse_board(company_name: str, board_token: str) -> List[NormalizedJobPost]:
    """Fetches all live technical and AI roles from a Greenhouse board."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    posts = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            res = await client.get(url)
            if res.status_code != 200:
                logger.warning(f"Failed to fetch {company_name} Greenhouse: {res.status_code}")
                return []
            
            data = res.json()
            jobs = data.get("jobs", [])
            logger.info(f"{company_name}: Retrieved {len(jobs)} live postings from Greenhouse API.")

            for j in jobs:
                title = j.get("title", "")
                loc = j.get("location", {}).get("name", "") if isinstance(j.get("location"), dict) else str(j.get("location", ""))
                jid = str(j.get("id", ""))
                canonical_url = j.get("absolute_url") or f"https://boards.greenhouse.io/{board_token}/jobs/{jid}"
                content_html = j.get("content", "")
                clean_text = clean_html_to_text(content_html) if content_html else f"{title} at {company_name}"
                content_hash = compute_content_hash(clean_text)

                posts.append(
                    NormalizedJobPost(
                        external_id=jid,
                        canonical_url=canonical_url,
                        company_name=company_name,
                        title=title,
                        location=loc or "Remote",
                        description_raw=content_html or clean_text,
                        description_text=clean_text,
                        content_hash=content_hash,
                    )
                )
    except Exception as e:
        logger.error(f"Error fetching {company_name}: {e}")

    return posts

async def main():
    logger.info("Starting Global Remote & Multi-Country Direct ATS Ingestion...")
    db = SessionLocal()
    provider = MockLLMProvider()

    all_posts: List[NormalizedJobPost] = []
    for comp_name, b_token in GREENHOUSE_BOARDS:
        posts = await fetch_greenhouse_board(comp_name, b_token)
        all_posts.extend(posts)

    logger.info(f"Total ATS posts retrieved: {len(all_posts)}. Saving and analyzing in DB...")

    saved = 0
    junior_saved = 0
    remote_saved = 0

    for post in all_posts:
        job, is_new = save_normalized_job(db, post)
        analysis = await extract_and_save_job(db, job, provider)
        if analysis.is_relevant:
            saved += 1
            if analysis.seniority in ["junior", "intern"]:
                junior_saved += 1
            if "remote" in (job.location or "").lower() or "[r]" in (job.location or "").lower() or "remote" in job.title.lower():
                remote_saved += 1

    db.close()

    logger.info("=========================================")
    logger.info("🎉 GLOBAL DIRECT ATS INGESTION COMPLETE!")
    logger.info(f"Total Relevant Technical Jobs in DB: {saved}")
    logger.info(f"Junior / Intern Positions: {junior_saved}")
    logger.info(f"Remote Positions: {remote_saved}")
    logger.info("=========================================")

if __name__ == "__main__":
    asyncio.run(main())
