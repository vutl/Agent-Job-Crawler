import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.database import Base, get_db, Job, Company
from apps.api.main import app

def test_api_endpoints():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # Seed a test company and job
    db = TestingSession()
    c = Company(id="c1", name="Thumbtack", domain="thumbtack.com")
    db.add(c)
    db.commit()

    j = Job(
        id="j1",
        external_id="test_1",
        canonical_url="https://jobs.ashbyhq.com/thumbtack/123",
        company_id="c1",
        title="Software Engineer, AI/ML Infrastructure",
        location="United States",
        description_raw="<p>Python and PyTorch</p>",
        description_text="Python and PyTorch",
        content_hash="hash123",
    )
    db.add(j)
    db.commit()

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. Data freshness
    res = client.get("/system/data-freshness")
    assert res.status_code == 200
    assert res.json()["total_jobs"] == 1

    # 3. Roles list
    res = client.get("/roles")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 4. Jobs list endpoint
    res = client.get("/api/v1/jobs")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Software Engineer, AI/ML Infrastructure"
    assert data["items"][0]["company_name"] == "Thumbtack"
    assert data["items"][0]["canonical_url"] == "https://jobs.ashbyhq.com/thumbtack/123"

    app.dependency_overrides.clear()
