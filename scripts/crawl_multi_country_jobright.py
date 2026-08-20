import asyncio
import httpx
import re
import os
import sys
import logging
from typing import List, Set, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import SessionLocal, Job, Company
from packages.schemas import NormalizedJobPost
from apps.crawler.normalizer import clean_html_to_text, normalize_canonical_url, compute_content_hash
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job
from apps.crawler.monitors.jobright import JobrightMonitor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("multi_country_jobright")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://jobright.ai",
    "Referer": "https://jobright.ai/jobs/recommend",
    "Content-Type": "application/json",
}

async def crawl_and_expand_jobright(max_seeds: int = 120):
    """
    Crawls Jobright deeply via recursive multi-hop similar jobs discovery.
    Extracts authentic employer postings across all target countries & roles.
    """
    logger.info("Starting deep multi-country recursive crawl for Jobright...")
    
    seen_ids: Set[str] = set()
    raw_jobs: List[Dict[str, Any]] = []
    queue: List[str] = []

    async with httpx.AsyncClient(headers=HEADERS, timeout=12.0) as client:
        # 1. Seed with Landing Recommendations
        try:
            r = await client.get("https://swan-api.jobright.ai/swan/recommend/landing/jobs")
            if r.status_code == 200:
                data = r.json()
                for item in data.get("result", {}).get("jobList", []):
                    jr = item.get("jobResult", {})
                    jid = jr.get("jobId")
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        raw_jobs.append(jr)
                        queue.append(jid)
            logger.info(f"Loaded {len(queue)} initial seed jobs from landing endpoint.")
        except Exception as e:
            logger.error(f"Failed to fetch landing jobs: {e}")

        # 2. Multi-hop recursive expansion
        processed_seeds = 0
        while queue and processed_seeds < max_seeds:
            curr_id = queue.pop(0)
            processed_seeds += 1

            if processed_seeds % 15 == 0 or processed_seeds == 1:
                logger.info(f"Progress: Processed {processed_seeds}/{max_seeds} seeds. Discovered {len(raw_jobs)} unique jobs...")

            try:
                s_res = await client.post(
                    "https://swan-api.jobright.ai/swan/recommend/similar/jobs",
                    json={"jobId": curr_id}
                )
                if s_res.status_code == 200:
                    s_data = s_res.json()
                    for item in s_data.get("result", {}).get("jobList", []):
                        jr = item.get("jobResult", {})
                        s_jid = jr.get("jobId")
                        if s_jid and s_jid not in seen_ids:
                            seen_ids.add(s_jid)
                            raw_jobs.append(jr)
                            queue.append(s_jid)
            except Exception as e:
                logger.debug(f"Error expanding seed {curr_id}: {e}")

    logger.info(f"Crawl finished. Total unique Jobright jobs collected: {len(raw_jobs)}")

    # 3. Normalize and save to database
    db = SessionLocal()
    monitor = JobrightMonitor()
    provider = MockLLMProvider()

    saved_count = 0
    junior_count = 0
    remote_count = 0

    for jr in raw_jobs:
        title = jr.get("jobTitle", "Untitled Role")
        company = monitor._extract_company_from_jobresult(jr)
        brand_company = f"Jobright | {company}" if company and not company.startswith("Jobright") else company
        job_id = str(jr.get("jobId", ""))
        raw_url = jr.get("applyLink") or jr.get("url") or f"https://jobright.ai/jobs/info/{job_id}"
        canonical_url = normalize_canonical_url(raw_url)

        # Detect remote status
        is_remote = (
            jr.get("isRemote") is True or
            "remote" in str(jr.get("workModel", "")).lower() or
            "remote" in str(jr.get("jobLocation", "")).lower() or
            "remote" in title.lower()
        )

        raw_loc = (jr.get("jobLocation") or "").strip()
        if is_remote:
            location = f"{raw_loc} (Remote)" if raw_loc and "remote" not in raw_loc.lower() else (raw_loc or "Remote")
            remote_count += 1
        else:
            location = raw_loc or "United States"

        summary = jr.get("jobSummary", "")
        responsibilities = jr.get("coreResponsibilities", [])
        salary = jr.get("salaryDesc", "")
        seniority = jr.get("jobSeniority", "")

        desc_parts = []
        if summary:
            desc_parts.append(summary)
        if salary:
            desc_parts.append(f"\n**Estimated Compensation**: {salary}")
        if seniority:
            desc_parts.append(f"**Experience Level**: {seniority}")
        if responsibilities:
            desc_parts.append("\n**Core Responsibilities**:")
            for r in responsibilities:
                desc_parts.append(f"- {r}")

        full_desc = "\n\n".join(desc_parts) if desc_parts else f"{title} at {company}"
        clean_text = clean_html_to_text(full_desc)
        content_hash = compute_content_hash(full_desc)

        norm_post = NormalizedJobPost(
            external_id=job_id,
            canonical_url=canonical_url,
            company_name=brand_company,
            title=title,
            location=location,
            description_raw=full_desc,
            description_text=clean_text,
            content_hash=content_hash,
        )

        db_job, is_new = save_normalized_job(db, norm_post)
        analysis = await extract_and_save_job(db, db_job, provider)
        saved_count += 1

        if analysis.seniority in ["junior", "intern"] and analysis.is_relevant:
            junior_count += 1

    db.close()

    logger.info("=========================================")
    logger.info(f"Deep Jobright Crawl Complete!")
    logger.info(f"Total Jobs Upserted & Analyzed: {saved_count}")
    logger.info(f"Junior / Intern Active Roles: {junior_count}")
    logger.info(f"Remote Positions Detected: {remote_count}")
    logger.info("=========================================")

if __name__ == "__main__":
    asyncio.run(crawl_and_expand_jobright(max_seeds=100))
