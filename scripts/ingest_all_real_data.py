import asyncio
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import Base, engine, SessionLocal, Job, Skill, JobSkill, JobAnalysis
from packages.schemas import NormalizedJobPost, SeniorityLevel
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
    print("Initializing Database tables for 500+ job ingestion across ALL sources & snapshots...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    provider = MockLLMProvider()

    count_saved = 0
    foorilla_mon = FoorillaMonitor()

    # 1. Parse Detailed Snapshot Files (format.txt, format2.txt, format3.txt)
    for snap_id, file_name in enumerate(["format.txt", "format2.txt", "format3.txt"], 1):
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as f:
                snap_html = f.read()
            post = foorilla_mon.parse_foorilla_html_snapshot(snap_html, source_name="Nokia Bell Labs", snapshot_id=str(snap_id))
            if post:
                job, is_new = save_normalized_job(db, post)
                if is_new:
                    count_saved += 1
                    await extract_and_save_job(db, job, provider)
            print(f"Parsed & ingested snapshot file {file_name} (Foorilla | Nokia Bell Labs)...")

    # 2. Add Leiden University Junior RSE (Direct Employer Forward)
    leiden_jd = """### Description
The Institute of Environmental Science CML at Leiden University is looking for a motivated Junior Research Software Engineer (RSE) with experience in full-stack development, data visualization, and modern software engineering practices to turn scientific insights into reliable and user-friendly software. In this role, you will help design, build, and maintain the next generation of industrial ecology research tools that support sustainability, circular economy analysis and decision making, as well as reproducible science across the institute. You will work closely with researchers to help create dashboards, APIs, and visual analytics that communicate scientific results to academic users, policymakers, and the wider public.

### What You Will Do
- Building and maintaining scientific software, web applications and dashboards for research dissemination and policy communication (e.g., WISE database, Activity Browser, Panorama web-app, ReLab).
- Supporting the development and maintenance of data pipelines and reproducible workflows for environmental databases and analytics.
- Collaborating with researchers to scope features, translate research needs into user-friendly tools, and ensure usability and accessibility.
- Supporting deployment in cloud and/or open environments (e.g., containerized services), working with the senior RSE on infrastructure alignment.
- Promoting good data and software management for FAIR and open science practices, version control (Git/GitHub), testing (pytest), packaging, documentation.

### Where You Will Work
Leiden University is situated between Amsterdam and The Hague and was founded in 1575, making it the oldest university in the Netherlands. The Institute of Environmental Science (CML) offers a vibrant and supportive community of scientists committed to the challenges of sustainability.

### What You Bring
- MSc in computer science, data science, AI, environmental informatics, or related field.
- Good programming skills with Python and JavaScript/TypeScript.
- Experience with front‑end frameworks (React) and data visualization (D3/Plotly).
- Experience building back‑end APIs (FastAPI, Django, Flask) and integrating databases (SQL/NoSQL).
- Experience contributing to open‑source projects.
- Familiarity with containerization (Docker) and reproducibility tools.

### What We Offer
- Salary ranges from € 3.708 to € 5.057 gross per month based on full-time position (38h/week).
- Holiday allowance (8%) and end-of-year bonus (8.3%).
- Attractive pension scheme with ABP.
- Hybrid working options & home-working allowance."""

    leiden_post = NormalizedJobPost(
        external_id="foorilla_leiden_3486317",
        canonical_url="https://careers.universiteitleiden.nl/job/Leiden-Junior-Research-Software-Engineer-for-Sustainability-Science-Full-Stack/16684-en_US/",
        company_name="Foorilla | Leiden University",
        company_domain="universiteitleiden.nl",
        title="Junior Research Software Engineer for Sustainability Science - Full Stack",
        location="Leiden, NL / Hybrid",
        description_raw=f"<p>{leiden_jd}</p>",
        description_text=leiden_jd,
        content_hash=compute_content_hash(leiden_jd),
    )
    job, is_new = save_normalized_job(db, leiden_post)
    if is_new:
        count_saved += 1
        await extract_and_save_job(db, job, provider)
    print("Parsed & ingested Leiden University Junior RSE (Foorilla | Leiden University)...")

    # 3. Parse Foorilla format4.txt (88 raw items)
    if os.path.exists("format4.txt"):
        with open("format4.txt", "r", encoding="utf-8") as f:
            f4_html = f.read()

        f4_raw_items = foorilla_mon.parse_job_items_from_html(f4_html)
        print(f"Parsed {len(f4_raw_items)} raw job items from format4.txt...")

        for idx, item in enumerate(f4_raw_items, 1):
            title = item.get("title", "Software Engineer")
            location = item.get("location", "Remote")
            level_code = item.get("level_code", "")
            detail_path = item.get("detail_path", "")

            # Ignore placeholder b...
            if title == "b..." or len(title) < 4:
                continue

            company = "Foorilla | Partner"
            link = f"https://foorilla.com{detail_path}" if detail_path.startswith("/") else "https://foorilla.com/hiring/jobs/?topic=data-ai-and-machine-learning"

            desc_text = f"### Description\n{title} at {company}.\n\n### Location & Mode\n- Location: {location}\n- Level: {level_code} {item.get('remote_code', '')}\n\n### Requirements\n- Experience with Python, PyTorch, SQL, Cloud infrastructure."
            
            post = NormalizedJobPost(
                external_id=f"foorilla_f4_{idx}",
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

    # 4. Parse Jobright format_jobright.txt (7 jobs)
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

    # 5. Parse Greenhouse fixture (299 Cloudflare jobs)
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

    # 6. Parse Lever fixture (103 Spotify jobs)
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
    print(f"🎉 INGESTION COMPLETE ACROSS ALL SOURCES!")
    print(f"Total Jobs in Database: {total_jobs}")
    print(f"Total Unique Extracted Skills: {total_skills}")
    print(f"Total Analyzed Jobs: {total_analyses}")
    print("=========================================\n")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
