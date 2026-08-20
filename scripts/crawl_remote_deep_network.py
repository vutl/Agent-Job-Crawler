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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("crawl_remote_deep_network")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://jobright.ai",
    "Referer": "https://jobright.ai/jobs/recommend",
    "Content-Type": "application/json",
}

# Authentic Remote Seed Job IDs across US, Canada, Australia, UK
REMOTE_SEEDS = [
    "6a86048a74e02153f1459e14", # Agility PR Solutions (Junior AI Software Engineer, Canada Remote)
    "6a57eb4c3330ca6f993c1fb5", # Cohere (ML Intern/Co-op, Canada Remote)
    "6a872fba25fc4e7ae3dabcd0", # GigFinder.ai (Data Scientist AI Evaluation, US Remote)
    "6a06f9344a0a6a7e7d81d22d", # StackAdapt (Software Engineer Stats & Analytics, Canada Remote)
    "6a86ea5425fc4e7ae3daa620",
    "6a86ea6c680f314a29d3602e",
    "6a74cdbfbb6ca93ae560bf89",
    "6a860ad4d34f700f87fbfd01",
    "6a6a520419d76667a2abefc9",
    "6a4d801c0209ea6fd6852884",
]

# Explicit verified remote postings from user's inspection
VERIFIED_MANUAL_POSTS = [
    {
        "external_id": "6a86048a74e02153f1459e14",
        "title": "Junior AI Software Engineer",
        "company": "Jobright | Agility PR Solutions",
        "domain": "agilitypr.com",
        "location": "Canada (Remote)",
        "url": "https://ats.rippling.com/agilitypr/jobs/63e3fac5-86e9-4b33-9881-7c4390da108b?jr_id=6a86048a74e02153f1459e14",
        "seniority": "Junior / Entry Level",
        "job_type": "Full-time",
        "salary": "$65,000 - $75,000/yr",
        "description": """### Overview
Agility PR Solutions provides an AI-native platform for media outreach, monitoring, and intelligence. The company is seeking a Junior AI Software Engineer to build agentic workflows and AI-driven applications, develop backend systems and RESTful APIs, integrate large language models, and collaborate across engineering and product teams.

- **Location**: Canada (100% Fully Remote Work Environment)
- **Employment Type**: Full-time (Salary: $65K/yr - $75K/yr)
- **Experience Level**: Entry Level / Junior
- **Jobright Link**: [View on Jobright](https://jobright.ai/jobs/info/6a86048a74e02153f1459e14#overview)
- **Official Rippling ATS**: [Apply on Rippling](https://ats.rippling.com/agilitypr/jobs/63e3fac5-86e9-4b33-9881-7c4390da108b?jr_id=6a86048a74e02153f1459e14)

### Responsibilities
- Develop code using an Agile development process and build new features for AI intelligence platforms.
- Design and implement RESTful API services (primarily in Java).
- Design and implement agentic workflows and AI-driven agents using TypeScript and Nest.js.
- Integrate with Large Language Models (LLMs) utilizing modern agent frameworks such as LangChain and/or LangGraph.
- Collaborate across backend, frontend, and product teams to ensure code quality through testing, reviews, and best practices.

### Qualifications & Required Skills
- Degree in Computer Science or a related field (Junior / New Grad).
- Hands-on experience with Java development and REST APIs.
- Working knowledge of TypeScript / JavaScript and Nest.js.
- Familiarity with AI/ML integrations, LLMs, and agentic frameworks (LangChain, LangGraph).
- Problem-solving skills with SQL, Linux, Git, and Maven.

### Preferred Experience
- Experience with agent orchestration patterns or workflow engines.
- Exposure to prompt engineering, evaluation techniques, and distributed big data systems (Hadoop, Solr).

### Benefits & Work Culture
- Fully remote work environment.
- Health, Dental & Vision benefits + RRSP matching and Life Insurance.
- Flex Fridays in Summer, Week off between Christmas and New Year's, and No Internal Meetings Fridays."""
    }
]

async def crawl_and_expand_remote_network(max_seeds: int = 100):
    """
    Crawls Jobright deeply starting from remote anchor seeds,
    discovering all authentic Remote tech postings across CA, US, AU, UK.
    """
    logger.info("Starting Deep Remote Jobright Network Crawl...")
    
    seen_ids: Set[str] = set()
    discovered_items: List[Dict[str, Any]] = []
    queue: List[str] = list(REMOTE_SEEDS)

    for s in REMOTE_SEEDS:
        seen_ids.add(s)

    async with httpx.AsyncClient(headers=HEADERS, timeout=12.0) as client:
        # Also grab landing jobs
        try:
            r = await client.get("https://swan-api.jobright.ai/swan/recommend/landing/jobs")
            if r.status_code == 200:
                data = r.json()
                for item in data.get("result", {}).get("jobList", []):
                    jr = item.get("jobResult", {})
                    jid = jr.get("jobId")
                    if jid and jid not in seen_ids:
                        seen_ids.add(jid)
                        discovered_items.append(item)
                        queue.append(jid)
        except Exception as e:
            logger.debug(f"Landing fetch error: {e}")

        # Expand similar jobs
        processed = 0
        while queue and processed < max_seeds:
            curr_id = queue.pop(0)
            processed += 1

            if processed % 15 == 0 or processed == 1:
                logger.info(f"Progress: Processed {processed}/{max_seeds} seeds. Total items discovered: {len(discovered_items)}...")

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
                            discovered_items.append(item)
                            queue.append(s_jid)
            except Exception as e:
                logger.debug(f"Error on seed {curr_id}: {e}")

    logger.info(f"Crawler collected {len(discovered_items)} raw items from Jobright network. Saving to DB...")

    db = SessionLocal()
    provider = MockLLMProvider()

    # 1. Save manual verified posts first
    for mp in VERIFIED_MANUAL_POSTS:
        full_desc = mp["description"]
        clean_text = clean_html_to_text(full_desc)
        content_hash = compute_content_hash(clean_text)

        norm_post = NormalizedJobPost(
            external_id=mp["external_id"],
            canonical_url=normalize_canonical_url(mp["url"]),
            company_name=mp["company"],
            title=mp["title"],
            location=mp["location"],
            description_raw=full_desc,
            description_text=clean_text,
            content_hash=content_hash,
        )
        db_job, is_new = save_normalized_job(db, norm_post)
        await extract_and_save_job(db, db_job, provider)
        logger.info(f"Saved Verified Post: '{db_job.title}' ({db_job.company.name}) | Loc: {db_job.location}")

    # 2. Save all crawled items
    saved_count = 0
    remote_saved = 0

    for item in discovered_items:
        jr = item.get("jobResult", {})
        cr = item.get("companyResult") or {}

        title = jr.get("jobTitle") or "Software Engineer"
        jid = jr.get("jobId") or ""
        if not jid:
            continue

        raw_company = cr.get("companyName") or jr.get("companyAlias") or jr.get("companyName") or "Technology Company"
        company_name = f"Jobright | {raw_company}" if not raw_company.startswith("Jobright") else raw_company
        domain = cr.get("companyURL") or ""

        # Determine Remote
        is_remote = (
            jr.get("isRemote") is True or
            "remote" in str(jr.get("workModel", "")).lower() or
            "remote" in str(jr.get("jobLocation", "")).lower() or
            "remote" in title.lower() or
            "remote" in str(jr.get("jobSummary", "")).lower()
        )

        raw_loc = (jr.get("jobLocation") or cr.get("companyLocation") or "Remote").strip()
        if is_remote:
            location = f"{raw_loc} (Remote)" if "remote" not in raw_loc.lower() else raw_loc
            remote_saved += 1
        else:
            location = raw_loc

        # Deep link URL
        raw_apply = jr.get("applyLink") or f"https://jobright.ai/jobs/info/{jid}#overview"
        canonical_url = normalize_canonical_url(raw_apply)

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

        full_desc = "\n\n".join(desc_parts) if desc_parts else f"{title} at {raw_company}"
        clean_text = clean_html_to_text(full_desc)
        content_hash = compute_content_hash(clean_text)

        norm_post = NormalizedJobPost(
            external_id=jid,
            canonical_url=canonical_url,
            company_name=company_name,
            title=title,
            location=location,
            description_raw=full_desc,
            description_text=clean_text,
            content_hash=content_hash,
        )

        db_job, is_new = save_normalized_job(db, norm_post)
        analysis = await extract_and_save_job(db, db_job, provider)
        if analysis.is_relevant:
            saved_count += 1

    db.close()

    logger.info("=========================================")
    logger.info("🎉 DEEP REMOTE JOBRIGHT CRAWL COMPLETE!")
    logger.info(f"Total Relevant Technical Jobs Ingested: {saved_count}")
    logger.info(f"Remote Positions Flagged: {remote_saved}")
    logger.info("=========================================")

if __name__ == "__main__":
    asyncio.run(crawl_and_expand_remote_network(max_seeds=80))
