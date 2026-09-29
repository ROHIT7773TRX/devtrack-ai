# ============================================================
# tests/unit/test_applications.py
# Unit tests for the DevTrack AI FastAPI backend.
#
# WHAT IS A UNIT TEST?
#   A unit test tests ONE small unit of your application in isolation.
#   "Isolation" means we use a test database (SQLite in-memory),
#   not the real PostgreSQL, so tests are:
#   - Fast (no network calls)
#   - Predictable (fresh database every test)
#   - Independent (one test doesn't affect another)
#
# WHAT IS pytest?
#   pytest is a Python testing framework.
#   It finds functions that start with "test_" and runs them.
#   If a test raises an exception or an assertion fails, the test FAILS.
#   If it completes without errors, the test PASSES.
#
# HOW TO RUN:
#   pytest tests/unit/test_applications.py -v
#   (the -v flag shows verbose output — each test name with PASS/FAIL)
#
# WHAT IS A FIXTURE?
#   A fixture is a function that sets up test resources.
#   The @pytest.fixture decorator marks a function as a fixture.
#   Tests can request fixtures as parameters — pytest injects them.
# ============================================================

import pytest
import os
import sys

# ──────────────────────────────────────────────
# CRITICAL: Set test DATABASE_URL BEFORE importing anything from the app.
# This tells SQLAlchemy to use SQLite instead of PostgreSQL.
# If we set this AFTER importing, the engine is already created with psycopg2.
# ──────────────────────────────────────────────
os.environ["DATABASE_URL"] = "sqlite:///./test_devtrack.db"

# Add the backend to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app/backend"))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db



# ──────────────────────────────────────────────
# TEST DATABASE SETUP
# ──────────────────────────────────────────────

# Use SQLite in-memory database for testing.
# WHY SQLite instead of PostgreSQL?
# - SQLite runs in memory — no server needed, instant startup
# - Tests are self-contained — no external dependencies
# - Each test run starts with a clean, empty database
# - SQLAlchemy works with both, so our models work unchanged
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with multiple threads
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ──────────────────────────────────────────────
# FIXTURES
# ──────────────────────────────────────────────

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database with all tables for each test function.

    scope="function" means this fixture runs ONCE PER TEST.
    Every test gets a clean, empty database — tests don't interfere with each other.

    HOW IT WORKS:
    1. Create all tables (CREATE TABLE statements)
    2. Create a session
    3. Yield the session to the test
    4. Drop all tables (cleanup)

    The yield makes this a context manager — cleanup always runs after the test.
    """
    Base.metadata.create_all(bind=test_engine)   # Create tables
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)  # Clean up — drop all tables


@pytest.fixture(scope="function")
def client(db_session):
    """
    Creates a FastAPI TestClient that uses the test database.

    FastAPI's TestClient simulates HTTP requests without starting a real server.
    We override get_db() to use the test database instead of the real PostgreSQL.

    DEPENDENCY OVERRIDE:
    FastAPI has a dependency override mechanism. We tell FastAPI:
    "when a route needs get_db, use this test version instead."
    This is called DEPENDENCY INJECTION — a core FastAPI pattern.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # session is managed by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# HELPER: SAMPLE APPLICATION DATA
# ──────────────────────────────────────────────

def sample_application_data(**overrides):
    """
    Returns a dict of valid application data for use in tests.
    Pass keyword arguments to override specific fields.

    Usage:
        data = sample_application_data()  # all defaults
        data = sample_application_data(company_name="Microsoft")  # override one field
    """
    base = {
        "company_name": "Google",
        "role":         "Software Engineer",
        "location":     "Bangalore",
        "source":       "LinkedIn",
        "status":       "Applied",
        "applied_date": "2026-09-29",
        "notes":        "Applied through referral",
    }
    base.update(overrides)
    return base


# ──────────────────────────────────────────────
# TEST 1: Health check endpoint
# ──────────────────────────────────────────────
def test_health_check(client):
    """
    WHAT WE'RE TESTING:
    The /health endpoint should return 200 OK with status "healthy".

    WHY THIS TEST?
    The health endpoint is critical — Kubernetes uses it for liveness probes.
    If this breaks, Kubernetes will restart the pod in a loop.
    """
    response = client.get("/health")

    # ASSERTION: assert stops the test with FAIL if the condition is False
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    data = response.json()
    assert data["status"] == "healthy", f"Expected 'healthy' but got {data['status']}"
    assert "service" in data, "Response should contain 'service' field"


# ──────────────────────────────────────────────
# TEST 2: Create application — valid data
# ──────────────────────────────────────────────
def test_create_application_success(client):
    """
    WHAT WE'RE TESTING:
    POST /applications with valid data should return 201 Created
    and the created application data.

    POSITIVE TEST: tests the happy path (valid input → success).
    """
    data = sample_application_data()
    response = client.post("/applications/", json=data)

    assert response.status_code == 201, f"Expected 201 Created but got {response.status_code}"

    created = response.json()
    assert created["company_name"] == "Google"
    assert created["role"]         == "Software Engineer"
    assert created["status"]       == "Applied"
    assert "id"         in created, "Response must include auto-generated id"
    assert "created_at" in created, "Response must include created_at timestamp"
    assert "updated_at" in created, "Response must include updated_at timestamp"


# ──────────────────────────────────────────────
# TEST 3: Create application — missing required field
# ──────────────────────────────────────────────
def test_create_application_missing_company_name(client):
    """
    WHAT WE'RE TESTING:
    POST /applications without company_name (a required field)
    should return 422 Unprocessable Entity.

    NEGATIVE TEST: tests that invalid input is rejected correctly.

    WHY 422?
    FastAPI + Pydantic automatically validate request bodies.
    If a required field is missing, FastAPI returns 422 with a clear
    error message explaining which field is missing and why.
    """
    # Missing company_name (required field)
    data = {
        "role":     "Software Engineer",
        "location": "Bangalore",
    }
    response = client.post("/applications/", json=data)

    assert response.status_code == 422, \
        f"Expected 422 Unprocessable Entity for missing required field, got {response.status_code}"


# ──────────────────────────────────────────────
# TEST 4: Get all applications — empty database
# ──────────────────────────────────────────────
def test_get_applications_empty(client):
    """
    WHAT WE'RE TESTING:
    GET /applications on an empty database should return 200 OK
    with an empty list (not an error).

    WHY THIS TEST?
    A common bug is returning 404 or an error when there's no data.
    An empty list is the CORRECT response when there are no applications.
    """
    response = client.get("/applications/")

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), f"Response should be a list, got {type(data)}"
    assert len(data) == 0, f"Expected empty list, got {len(data)} items"


# ──────────────────────────────────────────────
# TEST 5: Get all applications — with data
# ──────────────────────────────────────────────
def test_get_applications_with_data(client):
    """
    WHAT WE'RE TESTING:
    After creating 2 applications, GET /applications should return a list of 2.

    This tests that:
    1. Data persists within the same test (db session)
    2. The list endpoint correctly returns all created items
    """
    # Create two applications
    client.post("/applications/", json=sample_application_data(company_name="Google"))
    client.post("/applications/", json=sample_application_data(company_name="Microsoft"))

    response = client.get("/applications/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2, f"Expected 2 applications, got {len(data)}"

    # Verify company names are present
    company_names = [app["company_name"] for app in data]
    assert "Google"    in company_names
    assert "Microsoft" in company_names


# ──────────────────────────────────────────────
# TEST 6: Get application by ID — found
# ──────────────────────────────────────────────
def test_get_application_by_id_found(client):
    """
    WHAT WE'RE TESTING:
    GET /applications/{id} with a valid ID returns 200 OK
    with the correct application data.
    """
    # Create an application first
    create_response = client.post(
        "/applications/",
        json=sample_application_data(company_name="Amazon")
    )
    application_id = create_response.json()["id"]

    # Fetch it by ID
    response = client.get(f"/applications/{application_id}")

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    data = response.json()
    assert data["id"]           == application_id
    assert data["company_name"] == "Amazon"


# ──────────────────────────────────────────────
# TEST 7: Get application by ID — not found
# ──────────────────────────────────────────────
def test_get_application_by_id_not_found(client):
    """
    WHAT WE'RE TESTING:
    GET /applications/{id} with a non-existent ID returns 404 Not Found.

    NEGATIVE TEST: Tests error handling for missing resources.

    WHY 404 and not 500?
    404 = "resource not found" — this is expected behavior, not a server error.
    500 = "server crashed" — this means something unexpected went wrong.
    """
    response = client.get("/applications/99999")  # ID that doesn't exist

    assert response.status_code == 404, \
        f"Expected 404 Not Found for non-existent ID, got {response.status_code}"

    data = response.json()
    assert "detail" in data, "404 response should include a 'detail' error message"


# ──────────────────────────────────────────────
# TEST 8: Update application status
# ──────────────────────────────────────────────
def test_update_application_status(client):
    """
    WHAT WE'RE TESTING:
    PATCH /applications/{id} with a new status correctly updates it
    and returns the updated application.

    This simulates the real workflow: you apply (Applied),
    then get a call (Screening), then get an interview (Interview).
    """
    # Create application with initial status
    create_response = client.post(
        "/applications/",
        json=sample_application_data(status="Applied")
    )
    assert create_response.status_code == 201
    app_id = create_response.json()["id"]
    assert create_response.json()["status"] == "Applied"

    # Update only the status
    update_response = client.patch(
        f"/applications/{app_id}",
        json={"status": "Interview"}
    )

    assert update_response.status_code == 200, \
        f"Expected 200 on update, got {update_response.status_code}"

    updated = update_response.json()
    assert updated["status"]       == "Interview", f"Status should be 'Interview', got {updated['status']}"
    assert updated["company_name"] == "Google",    "company_name should be unchanged"


# ──────────────────────────────────────────────
# TEST 9: Delete application
# ──────────────────────────────────────────────
def test_delete_application(client):
    """
    WHAT WE'RE TESTING:
    DELETE /applications/{id} removes the application.
    A subsequent GET returns 404.

    Tests two things:
    1. DELETE returns 204 No Content (success, no body)
    2. After deletion, GET returns 404 (item is truly gone)
    """
    # Create
    create_response = client.post("/applications/", json=sample_application_data())
    app_id = create_response.json()["id"]

    # Delete
    delete_response = client.delete(f"/applications/{app_id}")
    assert delete_response.status_code == 204, \
        f"Expected 204 No Content on delete, got {delete_response.status_code}"

    # Verify it's gone
    get_response = client.get(f"/applications/{app_id}")
    assert get_response.status_code == 404, \
        f"Expected 404 after deletion, got {get_response.status_code}"


# ──────────────────────────────────────────────
# TEST 10: Dashboard with data
# ──────────────────────────────────────────────
def test_dashboard_with_applications(client):
    """
    WHAT WE'RE TESTING:
    GET /dashboard/ returns correct analytics after creating applications.

    Verifies:
    - total_applications count is correct
    - status_breakdown list is present
    - All required fields exist in the response
    """
    # Create 3 applications with different statuses
    client.post("/applications/", json=sample_application_data(company_name="Google",    status="Applied"))
    client.post("/applications/", json=sample_application_data(company_name="Amazon",    status="Interview"))
    client.post("/applications/", json=sample_application_data(company_name="Microsoft", status="Rejected"))

    response = client.get("/dashboard/")

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    data = response.json()

    # Verify structure
    assert "total_applications"     in data
    assert "active_applications"    in data
    assert "status_breakdown"       in data
    assert "recent_applications"    in data
    assert "applications_this_week" in data
    assert "offers_received"        in data
    assert "rejection_rate"         in data

    # Verify values
    assert data["total_applications"]  == 3, f"Expected 3 total, got {data['total_applications']}"
    assert data["active_applications"] == 2, \
        f"Expected 2 active (Google+Amazon), got {data['active_applications']}"
    assert data["rejection_rate"] > 0, "Rejection rate should be > 0 with one rejection"
