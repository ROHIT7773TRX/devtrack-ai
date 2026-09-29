# ============================================================
# tests/integration/test_api.py
# Integration tests exercising full multi-step API workflows.
#
# WHAT IS AN INTEGRATION TEST?
#   Unlike unit tests that test a single function/endpoint in isolation,
#   integration tests simulate real user multi-step scenarios:
#   1. User creates a job application
#   2. User views the dashboard to see application counts update
#   3. User updates status (Applied -> Interview)
#   4. User adds an interview round
#   5. User deletes the application and verifies counts revert
# ============================================================

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///./test_integration.db"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app/backend"))

from main import app
from database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_full_application_lifecycle_integration(client):
    """
    INTEGRATION WORKFLOW TEST:
    Tests the complete lifecycle of an application from creation to dashboard reflection,
    adding interview rounds, status updates, and final deletion.
    """
    # Step 1: Check initial dashboard state (empty)
    resp = client.get("/dashboard/")
    assert resp.status_code == 200
    assert resp.json()["total_applications"] == 0

    # Step 2: Create Application 1 (Microsoft)
    app1_data = {
        "company_name": "Microsoft",
        "role": "DevOps Engineer",
        "location": "Hyderabad",
        "source": "LinkedIn",
        "status": "Applied",
        "applied_date": "2026-09-29"
    }
    create_resp = client.post("/applications/", json=app1_data)
    assert create_resp.status_code == 201
    app1_id = create_resp.json()["id"]

    # Step 3: Verify dashboard count increased to 1
    resp = client.get("/dashboard/")
    assert resp.json()["total_applications"] == 1
    assert resp.json()["active_applications"] == 1

    # Step 4: Add an Interview Round for Application 1
    interview_data = {
        "round_number": 1,
        "interview_type": "Technical",
        "scheduled_at": "2026-10-02T10:00:00",
        "outcome": "Pending",
        "notes": "Terraform and K8s questions"
    }
    round_resp = client.post(f"/applications/{app1_id}/interviews", json=interview_data)
    assert round_resp.status_code == 201
    assert round_resp.json()["application_id"] == app1_id

    # Step 5: Update Application status to "Interview"
    patch_resp = client.patch(f"/applications/{app1_id}", json={"status": "Interview"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "Interview"

    # Step 6: Verify detailed application fetch includes the interview round
    detail_resp = client.get(f"/applications/{app1_id}")
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["interview_rounds"]) == 1
    assert detail_resp.json()["interview_rounds"][0]["interview_type"] == "Technical"

    # Step 7: Delete application and verify cascade deletion
    del_resp = client.delete(f"/applications/{app1_id}")
    assert del_resp.status_code == 204

    # Step 8: Dashboard count should be 0 again
    resp_after = client.get("/dashboard/")
    assert resp_after.json()["total_applications"] == 0
