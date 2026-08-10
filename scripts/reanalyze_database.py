import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import Base, engine, SessionLocal, Job
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.extractor import extract_and_save_job

async def main():
    print("Re-evaluating all jobs in database with strict non-core role filter...")
    db = SessionLocal()
    provider = MockLLMProvider()

    jobs = db.query(Job).all()
    print(f"Found {len(jobs)} total jobs in database to re-evaluate...")

    reclassified_non_relevant = 0
    for job in jobs:
        analysis = await extract_and_save_job(db, job, provider)
        if not analysis.is_relevant:
            reclassified_non_relevant += 1

    print("\n=========================================")
    print(f"🎉 RE-ANALYSIS COMPLETE!")
    print(f"Total Jobs Re-analyzed: {len(jobs)}")
    print(f"Jobs classified as Non-Core / Non-Relevant: {reclassified_non_relevant}")
    print("=========================================\n")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
