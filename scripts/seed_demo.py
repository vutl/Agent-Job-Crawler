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
from apps.analyzer.provider import MockLLMProvider, OpenAICompatibleProvider
from apps.analyzer.extractor import extract_and_save_job

async def main():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")

    if api_key and base_url:
        print(f"Using OpenAICompatibleProvider (9Router / Antigravity) at {base_url} model={model}...")
        provider = OpenAICompatibleProvider(base_url=base_url, api_key=api_key, model=model)
    else:
        print("Using MockLLMProvider for offline seeding...")
        provider = MockLLMProvider()

    # 1. Load Greenhouse fixture
    if os.path.exists("tests/fixtures/greenhouse_jobs.json"):
        with open("tests/fixtures/greenhouse_jobs.json") as f:
            gh_data = json.load(f)

        for item in gh_data.get("jobs", []):
            raw_html = item.get("content", "")
            plain_text = clean_html_to_text(raw_html)
            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=normalize_canonical_url(item.get("absolute_url", "")),
                company_name="Acme AI",
                company_domain="acme.com",
                title=item.get("title", ""),
                location=item.get("location", {}).get("name"),
                description_raw=raw_html,
                description_text=plain_text,
                content_hash=compute_content_hash(plain_text),
            )
            job, is_new = save_normalized_job(db, post)
            if is_new:
                print(f"[Greenhouse] Saved new job: {job.title}")
                analysis = await extract_and_save_job(db, job, provider)
                print(f" -> Extracted role: {analysis.role_family}")

    # 2. Load Lever fixture
    if os.path.exists("tests/fixtures/lever_jobs.json"):
        with open("tests/fixtures/lever_jobs.json") as f:
            lever_data = json.load(f)

        for item in lever_data:
            desc_raw = item.get("description", "")
            for lst in item.get("lists", []):
                desc_raw += f"\n<h3>{lst.get('text', '')}</h3>\n{lst.get('content', '')}"
            plain_text = clean_html_to_text(desc_raw)
            post = NormalizedJobPost(
                external_id=str(item.get("id")),
                canonical_url=normalize_canonical_url(item.get("hostedUrl", "")),
                company_name="TechCorp",
                company_domain="techcorp.com",
                title=item.get("text", ""),
                location=item.get("categories", {}).get("location"),
                description_raw=desc_raw,
                description_text=plain_text,
                content_hash=compute_content_hash(plain_text),
            )
            job, is_new = save_normalized_job(db, post)
            if is_new:
                print(f"[Lever] Saved new job: {job.title}")
                analysis = await extract_and_save_job(db, job, provider)
                print(f" -> Extracted role: {analysis.role_family}")

    # 3. Load TopCV sample fixture
    if os.path.exists("tests/fixtures/topcv/detail_sample.html"):
        with open("tests/fixtures/topcv/detail_sample.html", encoding="utf-8") as f:
            topcv_html = f.read()

        topcv_monitor = TopCVMonitor()
        meta, desc_raw, desc_text = topcv_monitor.parse_job_detail(
            topcv_html,
            fallback_title="AI Team Leader",
            fallback_company="ACWORKS VIETNAM",
        )
        post = NormalizedJobPost(
            external_id="2121776",
            canonical_url="https://www.topcv.vn/viec-lam/ai-team-leader-branch-manager-ha-noi/2121776.html",
            company_name=meta["company"],
            company_domain="topcv.vn",
            title=meta["title"],
            location=meta["location"] or "Hà Nội",
            description_raw=desc_raw,
            description_text=desc_text,
            content_hash=compute_content_hash(desc_text),
        )
        job, is_new = save_normalized_job(db, post)
        if is_new:
            print(f"[TopCV] Saved new job: {job.title}")
            analysis = await extract_and_save_job(db, job, provider)
            print(f" -> Extracted role: {analysis.role_family}")

    # 4. Load Foorilla Nokia sample fixture (format2.txt)
    if os.path.exists("format2.txt"):
        with open("format2.txt", encoding="utf-8") as f:
            foorilla_html = f.read()

        foorilla_monitor = FoorillaMonitor()
        foorilla_post = foorilla_monitor.parse_foorilla_html_snapshot(foorilla_html, source_name="Nokia")
        if foorilla_post:
            job, is_new = save_normalized_job(db, foorilla_post)
            if is_new:
                print(f"[Foorilla] Saved new job: {job.title}")
                analysis = await extract_and_save_job(db, job, provider)
                print(f" -> Extracted role: {analysis.role_family}")

    total_jobs = db.query(Job).count()
    total_skills = db.query(Skill).count()
    total_analyses = db.query(JobAnalysis).count()

    print("\n--- Seeding Summary ---")
    print(f"Total Jobs: {total_jobs}")
    print(f"Total Unique Skills: {total_skills}")
    print(f"Total Analyzed Jobs: {total_analyses}")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
