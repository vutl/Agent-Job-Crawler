import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import Base, engine, SessionLocal, Job, Skill, JobSkill, JobAnalysis
from apps.crawler.monitors.greenhouse import GreenhouseMonitor
from apps.crawler.monitors.lever import LeverMonitor
from apps.crawler.monitors.workday import WorkdayMonitor
from apps.crawler.monitors.foorilla import FoorillaMonitor
from apps.crawler.monitors.jobright import JobrightMonitor
from apps.crawler.store import save_normalized_job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

async def main():
    print("==================================================")
    print("🚀 STARTING LIVE REMOTE CRAWL ACROSS ALL 6 MONITORS...")
    print("==================================================")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    provider = MockLLMProvider()

    # 1. Live Greenhouse (Cloudflare)
    print("\n[1/5] Fetching live Greenhouse jobs (Cloudflare)...")
    gh_mon = GreenhouseMonitor()
    gh_jobs = await gh_mon.fetch_jobs("Cloudflare", "cloudflare")
    print(f" -> Live Greenhouse returned {len(gh_jobs)} posts!")
    for post in gh_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 2. Live Lever (Spotify)
    print("\n[2/5] Fetching live Lever jobs (Spotify)...")
    lever_mon = LeverMonitor()
    lever_jobs = await lever_mon.fetch_jobs("Spotify", "spotify")
    print(f" -> Live Lever returned {len(lever_jobs)} posts!")
    for post in lever_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 3. Live Workday (DataRobot)
    print("\n[3/5] Fetching live Workday jobs (DataRobot)...")
    wd_mon = WorkdayMonitor()
    wd_jobs = await wd_mon.fetch_jobs("DataRobot", "datarobot/DataRobot_External_Careers")
    print(f" -> Live Workday returned {len(wd_jobs)} posts!")
    for post in wd_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 4. Live Foorilla (Data & AI Topics)
    print("\n[4/5] Fetching live Foorilla jobs (Data, AI & ML)...")
    foo_mon = FoorillaMonitor()
    foo_jobs = await foo_mon.fetch_jobs("Foorilla Aggregated", "data-ai-and-machine-learning")
    print(f" -> Live Foorilla returned {len(foo_jobs)} posts!")
    for post in foo_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    # 5. Live Jobright (Recommend)
    print("\n[5/5] Fetching live Jobright jobs (Recommend)...")
    jr_mon = JobrightMonitor()
    jr_jobs = await jr_mon.fetch_jobs("Jobright Aggregated", "recommend")
    print(f" -> Live Jobright returned {len(jr_jobs)} posts!")
    for post in jr_jobs:
        job, is_new = save_normalized_job(db, post)
        if is_new:
            await extract_and_save_job(db, job, provider)

    total_jobs = db.query(Job).count()
    total_skills = db.query(Skill).count()
    total_analyses = db.query(JobAnalysis).count()

    print("\n==================================================")
    print(f"🎉 LIVE CRAWL COMPLETE!")
    print(f"Total Live Jobs in Database: {total_jobs}")
    print(f"Total Unique Extracted Skills: {total_skills}")
    print(f"Total Analyzed Jobs: {total_analyses}")
    print("==================================================\n")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
