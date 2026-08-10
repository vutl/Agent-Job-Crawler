import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from packages.database import Base, Company, Job, JobSkill, JobAnalysis, Skill
from packages.schemas import RoleFamily
from apps.analyzer.provider import MockLLMProvider
from apps.analyzer.prefilter import is_prefilter_pass
from apps.analyzer.extractor import extract_and_save_job

def test_prefilter_rules():
    # 1. Non-tech title -> Instant rejection
    pass1, reason1 = is_prefilter_pass("Video AI Editor & Content Creator", "Edit videos for social media.")
    assert pass1 is False
    assert "non-technical pattern" in reason1

    # 2. Zero tech keywords -> Instant rejection
    pass2, reason2 = is_prefilter_pass("Senior Manager", "Manage office supplies and team schedules.")
    assert pass2 is False
    assert "Zero technical keywords" in reason2

    # 3. Valid tech job -> Passes prefilter
    pass3, reason3 = is_prefilter_pass("Software Engineer", "Build backend microservices in Python and SQL with Docker.")
    assert pass3 is True
    assert "Passed" in reason3

@pytest.mark.asyncio
async def test_extract_and_save_job():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    company = Company(name="AI Systems Inc.")
    db.add(company)
    db.flush()

    job = Job(
        canonical_url="https://jobs.aisystems.com/1",
        company_id=company.id,
        title="Senior AI Engineer",
        description_raw="<p>Must know PyTorch, FastAPI, Kubernetes, and AWS.</p>",
        description_text="Must know PyTorch, FastAPI, Kubernetes, and AWS.",
        content_hash="dummyhash123",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    provider = MockLLMProvider()
    analysis = await extract_and_save_job(db, job, provider)

    assert analysis.role_family == RoleFamily.AI_ENGINEER.value
    assert analysis.seniority == "senior"

    skills = db.query(Skill).all()
    skill_names = [s.canonical_name for s in skills]
    assert "PyTorch" in skill_names
    assert "Kubernetes" in skill_names
    assert "AWS" in skill_names
    assert "FastAPI" in skill_names

@pytest.mark.asyncio
async def test_non_technical_ai_role_filter():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    company = Company(name="Media Studio")
    db.add(company)
    db.flush()

    job = Job(
        canonical_url="https://jobs.mediastudio.com/editor",
        company_id=company.id,
        title="Video AI Editor & Content Creator",
        description_raw="<p>Edit short form videos using Runway, Midjourney, and ChatGPT.</p>",
        description_text="Edit short form videos using Runway, Midjourney, and ChatGPT.",
        content_hash="videoeditor123",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    provider = MockLLMProvider()
    analysis = await extract_and_save_job(db, job, provider)

    assert analysis.role_family == RoleFamily.NOT_RELEVANT.value
    assert analysis.model == "heuristic_prefilter"
    assert db.query(JobSkill).filter(JobSkill.job_id == job.id).count() == 0
