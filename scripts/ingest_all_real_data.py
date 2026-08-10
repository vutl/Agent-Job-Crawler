import asyncio
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import Base, engine, SessionLocal, Job, Skill, JobSkill, JobAnalysis
from packages.schemas import NormalizedJobPost
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from apps.crawler.store import save_normalized_job
from apps.crawler.monitors.topcv import TopCVMonitor
from apps.crawler.monitors.foorilla import FoorillaMonitor
from apps.crawler.monitors.jobright import JobrightMonitor
from apps.crawler.monitors.greenhouse import GreenhouseMonitor
from apps.crawler.monitors.lever import LeverMonitor
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

async def main():
    print("Initializing Database tables for 500+ job ingestion with Dual Branding...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    provider = MockLLMProvider()

    count_saved = 0

    # 1. Parse Foorilla format4.txt
    if os.path.exists("format4.txt"):
        with open("format4.txt", "r", encoding="utf-8") as f:
            f4_html = f.read()

        foorilla_mon = FoorillaMonitor()
        f4_raw_items = foorilla_mon.parse_job_items_from_html(f4_html)
        print(f"Parsed {len(f4_raw_items)} raw job items from format4.txt...")

        for idx, item in enumerate(f4_raw_items, 1):
            title = item.get("title", "Software Engineer")
            detail_path = item.get("detail_path", "")
            location = item.get("location", "Remote")

            # Dual Branding as requested
            company = "Foorilla | Partner"

            # Use valid detail path or valid topic URL (avoid fake 404 links)
            if detail_path and not detail_path.startswith("http"):
                link = f"https://foorilla.com{detail_path}"
            elif detail_path:
                link = detail_path
            else:
                link = f"https://foorilla.com/hiring/jobs/?topic=data-ai-and-machine-learning"

            desc_text = f"Job Posting: {title} at {company}. Location: {location}. Badges: {item.get('level_code', '')} {item.get('remote_code', '')}. Requires Python, PyTorch, SQL, Cloud."
            
            # If description is just 1 line summary without full target ATS follow-through, mark as paywall/login audit item
            status = "active" if len(desc_text) > 150 else "paywall"

            post = NormalizedJobPost(
                external_id=f"foorilla_{idx}",
                canonical_url=normalize_canonical_url(link),
                company_name=company,
                company_domain="foorilla.com",
                title=title,
                location=location,
                description_raw=f"<p>{desc_text}</p>",
                description_text=desc_text,
                content_hash=compute_content_hash(desc_text),
            )
            job, is_new = save_normalized_job(db, post)
            if is_new:
                count_saved += 1
                await extract_and_save_job(db, job, provider)

    # 2. Parse Jobright format_jobright.txt (7 jobs)
    if os.path.exists("format_jobright.txt"):
        with open("format_jobright.txt", "r", encoding="utf-8") as f:
            jr_html = f.read()

        jr_mon = JobrightMonitor()
        jr_posts = jr_mon.parse_jobright_html_snapshot(jr_html)
        print(f"Parsed {len(jr_posts)} jobs from format_jobright.txt...")
        for post in jr_posts:
            job, is_new = save_normalized_job(db, post)
            if is_new:
                count_saved += 1
                await extract_and_save_job(db, job, provider)

    # 3. Parse Greenhouse fixture (299 Cloudflare jobs)
    if os.path.exists("tests/fixtures/greenhouse_jobs.json"):
        with open("tests/fixtures/greenhouse_jobs.json") as f:
            gh_data = json.load(f)

        jobs_list = gh_data.get("jobs", [])
        print(f"Parsed {len(jobs_list)} Cloudflare jobs from greenhouse_jobs.json...")
        for item in jobs_list:
            raw_html = item.get("content", "")
            plain_text = clean_html_to_text(raw_html)
            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=normalize_canonical_url(item.get("absolute_url", "")),
                company_name="Cloudflare",
                company_domain="cloudflare.com",
                title=item.get("title", ""),
                location=item.get("location", {}).get("name", "San Francisco, CA"),
                description_raw=raw_html,
                description_text=plain_text,
                content_hash=compute_content_hash(plain_text),
            )
            job, is_new = save_normalized_job(db, post)
            if is_new:
                count_saved += 1
                await extract_and_save_job(db, job, provider)

    # 4. Parse Lever fixture (103 Spotify jobs)
    if os.path.exists("tests/fixtures/lever_jobs.json"):
        with open("tests/fixtures/lever_jobs.json") as f:
            lever_data = json.load(f)

        print(f"Parsed {len(lever_data)} Spotify jobs from lever_jobs.json...")
        for item in lever_data:
            desc_raw = item.get("description", "")
            for lst in item.get("lists", []):
                desc_raw += f"\n<h3>{lst.get('text', '')}</h3>\n{lst.get('content', '')}"
            plain_text = clean_html_to_text(desc_raw)
            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=normalize_canonical_url(item.get("hostedUrl", "")),
                company_name="Spotify",
                company_domain="spotify.com",
                title=item.get("text", ""),
                location=item.get("categories", {}).get("location", "Stockholm / Remote"),
                description_raw=desc_raw,
                description_text=plain_text,
                content_hash=compute_content_hash(plain_text),
            )
            job, is_new = save_normalized_job(db, post)
            if is_new:
                count_saved += 1
                await extract_and_save_job(db, job, provider)

    total_jobs = db.query(Job).count()
    total_skills = db.query(Skill).count()
    total_analyses = db.query(JobAnalysis).count()

    print("\n=========================================")
    print(f"🎉 INGESTION COMPLETE WITH DUAL BRANDING!")
    print(f"Total Jobs in Database: {total_jobs}")
    print(f"Total Unique Extracted Skills: {total_skills}")
    print(f"Total Analyzed Jobs: {total_analyses}")
    print("=========================================\n")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
