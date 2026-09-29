# ============================================================
# routers/applications.py
# API routes for job application CRUD operations.
#
# WHAT IS A ROUTER?
#   Instead of putting all routes in main.py (which would become
#   huge), we organize routes into separate router files.
#   This is like having separate chapters in a book.
#
#   main.py includes this router with:
#   app.include_router(applications.router)
#
# HTTP METHODS USED:
#   GET    → Read data (no side effects)
#   POST   → Create new data
#   PATCH  → Partially update existing data
#   DELETE → Remove data
#
# REST URL CONVENTION:
#   GET    /applications       → list all applications
#   POST   /applications       → create a new application
#   GET    /applications/{id}  → get one application by ID
#   PATCH  /applications/{id}  → update one application
#   DELETE /applications/{id}  → delete one application
# ============================================================

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

import models
import schemas
from database import get_db

# Create a router with a prefix so all URLs start with /applications
router = APIRouter(
    prefix="/applications",
    tags=["Applications"],  # Groups endpoints in the /docs page
)


# ──────────────────────────────────────────────
# GET /applications — List all applications
# ──────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[schemas.ApplicationSummary],
    summary="List all job applications"
)
def list_applications(
    status: Optional[models.ApplicationStatus] = Query(None, description="Filter by status"),
    skip:   int = Query(0,  ge=0,   description="Number of records to skip (pagination)"),
    limit:  int = Query(50, ge=1, le=200, description="Max records to return"),
    db:     Session = Depends(get_db)
):
    """
    Returns a list of all job applications.

    Optional query parameters:
    - **status**: filter by application status (e.g. ?status=Interview)
    - **skip**: for pagination — skip first N results
    - **limit**: max results to return (default 50)

    Example: GET /applications?status=Interview&limit=10
    """
    query = db.query(models.Application)

    # Apply optional status filter
    if status:
        query = query.filter(models.Application.status == status)

    # Order by most recently updated first
    query = query.order_by(desc(models.Application.updated_at))

    # Apply pagination
    applications = query.offset(skip).limit(limit).all()
    return applications


# ──────────────────────────────────────────────
# POST /applications — Create a new application
# ──────────────────────────────────────────────
@router.post(
    "/",
    response_model=schemas.ApplicationResponse,
    status_code=status.HTTP_201_CREATED,  # 201 = resource was CREATED (not just 200 OK)
    summary="Create a new job application"
)
def create_application(
    application: schemas.ApplicationCreate,
    db:          Session = Depends(get_db)
):
    """
    Creates a new job application record.

    Request body example:
    ```json
    {
        "company_name": "Google",
        "role": "Software Engineer",
        "location": "Bangalore",
        "source": "LinkedIn",
        "status": "Applied",
        "applied_date": "2026-09-29",
        "notes": "Applied through referral from college senior"
    }
    ```

    Returns the created application with its auto-generated id and timestamps.
    """
    # Create a new SQLAlchemy model instance from the Pydantic schema
    # model_dump() converts the Pydantic schema to a Python dict
    db_application = models.Application(**application.model_dump())

    # Stage the new record (tells SQLAlchemy to prepare the INSERT)
    db.add(db_application)

    # Execute the INSERT statement and commit the transaction
    db.commit()

    # Refresh to get the auto-generated values (id, created_at, updated_at)
    db.refresh(db_application)

    return db_application


# ──────────────────────────────────────────────
# GET /applications/{id} — Get one application
# ──────────────────────────────────────────────
@router.get(
    "/{application_id}",
    response_model=schemas.ApplicationResponse,
    summary="Get a specific job application by ID"
)
def get_application(
    application_id: int,
    db:             Session = Depends(get_db)
):
    """
    Returns a single job application by its ID.
    Includes all associated interview rounds.

    Returns 404 if the application does not exist.
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if not application:
        # HTTPException automatically returns the correct HTTP status code and JSON error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    return application


# ──────────────────────────────────────────────
# PATCH /applications/{id} — Update an application
# ──────────────────────────────────────────────
@router.patch(
    "/{application_id}",
    response_model=schemas.ApplicationResponse,
    summary="Update a job application (partial update)"
)
def update_application(
    application_id: int,
    updates:        schemas.ApplicationUpdate,
    db:             Session = Depends(get_db)
):
    """
    Partially updates a job application.
    Only fields provided in the request body are updated.
    Fields not included remain unchanged.

    Example: only update the status:
    ```json
    { "status": "Interview" }
    ```

    Returns 404 if the application does not exist.
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    # model_dump(exclude_unset=True) → returns ONLY the fields the user actually sent
    # This is what makes PATCH work: we only update what was provided
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application


# ──────────────────────────────────────────────
# DELETE /applications/{id} — Delete an application
# ──────────────────────────────────────────────
@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,  # 204 = success, no body returned
    summary="Delete a job application"
)
def delete_application(
    application_id: int,
    db:             Session = Depends(get_db)
):
    """
    Permanently deletes a job application and all its interview rounds.

    Returns 204 No Content on success (no response body).
    Returns 404 if the application does not exist.

    NOTE: This is irreversible. Interview rounds are cascade-deleted.
    """
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    db.delete(application)
    db.commit()
    # 204 No Content → return nothing (FastAPI handles this automatically)


# ──────────────────────────────────────────────
# POST /applications/{id}/interviews — Add interview round
# ──────────────────────────────────────────────
@router.post(
    "/{application_id}/interviews",
    response_model=schemas.InterviewRoundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an interview round to an application"
)
def create_interview_round(
    application_id: int,
    interview:      schemas.InterviewRoundCreate,
    db:             Session = Depends(get_db)
):
    """
    Adds a new interview round to a specific job application.

    Example:
    ```json
    {
        "round_number": 1,
        "interview_type": "Technical",
        "scheduled_at": "2026-10-05T14:00:00",
        "outcome": "Pending",
        "notes": "DSA + System Design round"
    }
    ```
    """
    # Verify the parent application exists
    application = db.query(models.Application).filter(
        models.Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with id {application_id} not found"
        )

    db_interview = models.InterviewRound(
        application_id=application_id,
        **interview.model_dump()
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)

    return db_interview


# ──────────────────────────────────────────────
# PATCH /applications/{id}/interviews/{round_id}
# Update an interview round outcome
# ──────────────────────────────────────────────
@router.patch(
    "/{application_id}/interviews/{round_id}",
    response_model=schemas.InterviewRoundResponse,
    summary="Update an interview round"
)
def update_interview_round(
    application_id: int,
    round_id:       int,
    updates:        schemas.InterviewRoundCreate,
    db:             Session = Depends(get_db)
):
    """Updates an interview round (e.g., set outcome after the interview)."""
    round_ = db.query(models.InterviewRound).filter(
        models.InterviewRound.id == round_id,
        models.InterviewRound.application_id == application_id
    ).first()

    if not round_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview round {round_id} not found for application {application_id}"
        )

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(round_, field, value)

    db.commit()
    db.refresh(round_)
    return round_
