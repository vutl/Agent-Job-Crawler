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
from apps.crawler.monitors.greenhouse import GreenhouseMonitor
from apps.crawler.monitors.lever import LeverMonitor
from apps.crawler.monitors.workday import WorkdayMonitor
from apps.crawler.monitors.foorilla import FoorillaMonitor
from apps.crawler.monitors.jobright import JobrightMonitor
from apps.crawler.monitors.topcv import TopCVMonitor
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

async def main():
    print("==================================================")
    print("🚀 STARTING COMPLETE CRAWL ACROSS ALL 6 MONITORS...")
    print("==================================================")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    provider = MockLLMProvider()

    # 1. Live Greenhouse (Cloudflare)
    print("\n[1/6] Fetching live Greenhouse jobs (Cloudflare)...")
    gh_mon = GreenhouseMonitor()
    gh_jobs = await gh_mon.fetch_jobs("Cloudflare", "cloudflare")
    print(f" -> Live Greenhouse returned {len(gh_jobs)} posts!")
    for post in gh_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 2. Live Lever (Spotify)
    print("\n[2/6] Fetching live Lever jobs (Spotify)...")
    lever_mon = LeverMonitor()
    lever_jobs = await lever_mon.fetch_jobs("Spotify", "spotify")
    print(f" -> Live Lever returned {len(lever_jobs)} posts!")
    for post in lever_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 3. Live Workday (DataRobot)
    print("\n[3/6] Fetching live Workday jobs (DataRobot)...")
    wd_mon = WorkdayMonitor()
    wd_jobs = await wd_mon.fetch_jobs("DataRobot", "datarobot/DataRobot_External_Careers")
    print(f" -> Live Workday returned {len(wd_jobs)} posts!")
    for post in wd_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 4. Foorilla (Data & AI Topics + Snapshots)
    print("\n[4/6] Fetching Foorilla jobs (Data, AI & ML + Nokia Bell Labs Snapshots)...")
    foo_mon = FoorillaMonitor()
    foo_jobs = await foo_mon.fetch_jobs("Foorilla Aggregated", "data-ai-and-machine-learning")
    print(f" -> Live Foorilla returned {len(foo_jobs)} posts!")
    for post in foo_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # Parse Foorilla Snapshots (format.txt, format2.txt, format3.txt, format4.txt)
    for snap_id, file_name in enumerate(["format.txt", "format2.txt", "format3.txt"], 1):
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                snap_html = f.read()
            post = foo_mon.parse_foorilla_html_snapshot(snap_html, source_name="Nokia Bell Labs", snapshot_id=str(snap_id))
            if post:
                job, is_new = save_normalized_job(db, post)
                if is_new:
                    await extract_and_save_job(db, job, provider)

    if os.path.exists("format4.txt"):
        with open("format4.txt", "r", encoding="utf-8") as f:
            f4_html = f.read()
        f4_raw_items = foo_mon.parse_job_items_from_html(f4_html)
        for idx, item in enumerate(f4_raw_items, 1):
            title = item.get("title", "Software Engineer")
            location = item.get("location", "Remote")
            company = "Foorilla | Partner"
            link = "https://foorilla.com/hiring/jobs/?topic=data-ai-and-machine-learning"
            desc_text = f"Job Posting: {title} at {company}. Location: {location}. Badges: {item.get('level_code', '')} {item.get('remote_code', '')}. Requires Python, PyTorch, SQL, Cloud."
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
                await extract_and_save_job(db, job, provider)

    # 5. Jobright (Recommend Feed + Snapshot)
    print("\n[5/6] Fetching Jobright jobs...")
    jr_mon = JobrightMonitor()
    jr_jobs = await jr_mon.fetch_jobs("Jobright Aggregated", "recommend")
    print(f" -> Live Jobright returned {len(jr_jobs)} posts!")
    for post in jr_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    if os.path.exists("format_jobright.txt"):
        with open("format_jobright.txt", "r", encoding="utf-8") as f:
            jr_html = f.read()
        jr_posts = jr_mon.parse_jobright_html_snapshot(jr_html)
        for post in jr_posts:
            job, is_new = save_normalized_job(db, post)
            if is_new:
                await extract_and_save_job(db, job, provider)

    # 6. TopCV (Vietnam AI / Data Jobs)
    print("\n[6/6] Fetching TopCV jobs (AI / Machine Learning / Data Science)...")
    topcv_mon = TopCVMonitor()
    try:
        topcv_jobs = await topcv_mon.fetch_jobs_by_keyword("AI Engineer", max_jobs=10)
        print(f" -> Live TopCV returned {len(topcv_jobs)} posts!")
        for post in topcv_jobs:
            job, is_new = save_normalized_job(db, post)
            if is_new:
                await extract_and_save_job(db, job, provider)
    except Exception as e:
        print(f" -> TopCV live fetch warning (network/captcha): {e}")

    total_jobs = db.query(Job).count()
    total_skills = db.query(Skill).count()
    total_analyses = db.query(JobAnalysis).count()

    print("\n==================================================")
    print(f"🎉 COMPLETE CRAWL & INGESTION FINISHED!")
    print(f"Total Jobs in Database: {total_jobs}")
    print(f"Total Unique Extracted Skills: {total_skills}")
    print(f"Total Analyzed Jobs: {total_analyses}")
    print("==================================================\n")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
