import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.database import Base, get_db
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

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

    # 2. Data freshness
    res = client.get("/system/data-freshness")
    assert res.status_code == 200
    assert res.json()["total_jobs"] == 0

    # 3. Roles list
    res = client.get("/roles")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    app.dependency_overrides.clear()
