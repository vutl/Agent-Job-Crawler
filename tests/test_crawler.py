import json
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from packages.database import Base, Company, Job
from packages.schemas import NormalizedJobPost
from apps.crawler.normalizer import clean_html_to_text, compute_content_hash, normalize_canonical_url
from apps.crawler.monitors.greenhouse import GreenhouseMonitor
from apps.crawler.monitors.lever import LeverMonitor
from apps.crawler.monitors.workday import WorkdayMonitor
from apps.crawler.monitors.foorilla import FoorillaMonitor
from apps.crawler.monitors.jobright import JobrightMonitor
from apps.crawler.store import save_normalized_job
from apps.crawler.worker import WorkerSettings

def test_normalizer():
    html = "<div><h1>Senior AI Engineer</h1><p>Experience with <b>PyTorch</b> and <b>Docker</b>.</p></div>"
    text = clean_html_to_text(html)
    assert "Senior AI Engineer" in text
    assert "PyTorch" in text
    assert "Docker" in text

    hash1 = compute_content_hash(text)
    hash2 = compute_content_hash(text + "   ")
    assert hash1 == hash2

    url = "https://boards.greenhouse.io/acme/jobs/12345?utm_source=linkedin#section"
    assert normalize_canonical_url(url) == "https://boards.greenhouse.io/acme/jobs/12345"

@pytest.mark.asyncio
async def test_greenhouse_monitor():
    with open("tests/fixtures/greenhouse_jobs.json") as f:
        fixture_data = json.load(f)

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = fixture_data

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        monitor = GreenhouseMonitor()
        jobs = await monitor.fetch_jobs("Acme Corp", "acme")

    assert len(jobs) == 2
    assert jobs[0].title == "Senior AI Engineer"
    assert jobs[0].canonical_url == "https://boards.greenhouse.io/acme/jobs/40101"
    assert "PyTorch" in jobs[0].description_text

@pytest.mark.asyncio
async def test_lever_monitor():
    with open("tests/fixtures/lever_jobs.json") as f:
        fixture_data = json.load(f)

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = fixture_data

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        monitor = LeverMonitor()
        jobs = await monitor.fetch_jobs("TechCorp", "techcorp")

    assert len(jobs) == 1
    assert jobs[0].title == "Lead Machine Learning Engineer"
    assert "PyTorch" in jobs[0].description_text

@pytest.mark.asyncio
async def test_workday_monitor():
    mock_list_res = MagicMock()
    mock_list_res.status_code = 200
    mock_list_res.json.return_value = {
        "jobPostings": [
            {
                "title": "Agentic AI Intern",
                "externalPath": "/job/Boston-MA/Agentic-AI-Intern_R-102729",
                "location": "Boston, MA"
            }
        ]
    }

    mock_detail_res = MagicMock()
    mock_detail_res.status_code = 200
    mock_detail_res.json.return_value = {
        "jobPostingInfo": {
            "title": "Agentic AI Intern",
            "jobDescription": "<p>Build LLM agents with PyTorch, LangChain, and Python.</p>",
            "location": "Boston, MA"
        }
    }

    async def mock_post_or_get(url, **kwargs):
        if url.endswith("/jobs"):
            return mock_list_res
        return mock_detail_res

    with patch("httpx.AsyncClient.post", side_effect=mock_post_or_get), \
         patch("httpx.AsyncClient.get", side_effect=mock_post_or_get):
        monitor = WorkdayMonitor()
        jobs = await monitor.fetch_jobs("DataRobot", "datarobot/DataRobot_External_Careers")

    assert len(jobs) == 1
    assert jobs[0].title == "Agentic AI Intern"
    assert "datarobot.wd1.myworkdayjobs.com" in jobs[0].canonical_url
    assert "PyTorch" in jobs[0].description_text

def test_foorilla_parser():
    with open("format2.txt", "r", encoding="utf-8") as f:
        html_content = f.read()

    monitor = FoorillaMonitor()
    job = monitor.parse_foorilla_html_snapshot(html_content, source_name="Nokia")
    assert job is not None
    assert job.title == "AI R&D Engineering Co-op"
    assert "PyTorch" in job.description_text
    assert "TensorFlow" in job.description_text

def test_foorilla_junior_remote_list_parser():
    with open("format4.txt", "r", encoding="utf-8") as f:
        html_content = f.read()

    monitor = FoorillaMonitor()
    all_jobs = monitor.parse_job_items_from_html(html_content)
    assert len(all_jobs) == 88

    junior_remote_jobs = monitor.parse_job_items_from_html(html_content, filter_junior_only=True, filter_remote_only=True)
    assert len(junior_remote_jobs) > 0
    titles = [j["title"] for j in junior_remote_jobs]
    assert "Machine Learning Engineer - New Grad 2026" in titles

def test_jobright_parser():
    with open("format_jobright.txt", "r", encoding="utf-8") as f:
        html_content = f.read()

    monitor = JobrightMonitor()
    jobs = monitor.parse_jobright_html_snapshot(html_content)
    assert len(jobs) == 7
    titles = [j.title for j in jobs]
    assert "AI Engineer – Entry Level" in titles
    assert "AI & ML Engineer" in titles

def test_jobright_detail_panel_json_parser():
    sample_html = '''
    <html>
    <head>
    <title>Software Engineer, AI/ML Infrastructure (US-Based) @ Thumbtack | Jobright.ai</title>
    <script id="jobright-helper-job-detail-info" type="application/json">
    {"jobResult":{"jobId":"6a0651eea88ea73abf7fa9a9","jobTitle":"Software Engineer, AI/ML Infrastructure (US-Based)","jobLocation":"United States","isRemote":true,"originalUrl":"https://jobs.ashbyhq.com/thumbtack/3efb1a7b-cfaf-475a-86a9-abff37581b4b/application","companyResult":{"companyName":"Thumbtack"}}}
    </script>
    <script id="job-posting" type="application/ld+json">
    {"@context":"https://schema.org/","@type":"JobPosting","title":"Software Engineer, AI/ML Infrastructure","description":"<p>Build and evolve core AI platform capabilities using PyTorch, Go, and Python.</p>"}
    </script>
    </head>
    </html>
    '''

    monitor = JobrightMonitor()
    jobs = monitor.parse_jobright_html_snapshot(sample_html)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == "Software Engineer, AI/ML Infrastructure (US-Based)"
    assert job.company_name == "Thumbtack"
    assert "jobs.ashbyhq.com/thumbtack" in job.canonical_url
    assert "PyTorch" in job.description_text

def test_arq_worker_settings():
    assert len(WorkerSettings.functions) == 5
    func_names = [f.__name__ for f in WorkerSettings.functions]
    assert "crawl_greenhouse_task" in func_names
    assert "crawl_workday_task" in func_names
    assert "crawl_foorilla_task" in func_names
    assert "crawl_jobright_task" in func_names

def test_job_upsert_and_deduplication():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    post = NormalizedJobPost(
        external_id="101",
        canonical_url="https://jobs.example.com/101",
        company_name="TestCorp",
        title="AI Engineer",
        description_raw="<p>Python and PyTorch</p>",
        description_text="Python and PyTorch",
        content_hash=compute_content_hash("Python and PyTorch"),
    )

    # 1. First save -> should create new job
    job1, is_new1 = save_normalized_job(db, post)
    assert is_new1 is True
    assert db.query(Job).count() == 1

    # 2. Duplicate save from a different aggregator with SAME content_hash -> should return False for is_new
    post_from_foorilla = post.model_copy(update={
        "canonical_url": "https://foorilla.com/hiring/jobs/redirect-101",
    })
    job2, is_new2 = save_normalized_job(db, post_from_foorilla)
    assert is_new2 is False
    assert db.query(Job).count() == 1

    # 3. Save with updated content -> should detect change
    updated_post = post.model_copy(update={
        "description_text": "Python, PyTorch and Kubernetes",
        "content_hash": compute_content_hash("Python, PyTorch and Kubernetes"),
    })
    job3, is_new3 = save_normalized_job(db, updated_post)
    assert is_new3 is True
    assert db.query(Job).count() == 1
    assert "Kubernetes" in job3.description_text
