# ============================================================
# schemas.py
# Pydantic schemas for request validation and response shaping.
#
# WHAT IS A SCHEMA (vs a MODEL)?
#
#   models.py  → SQLAlchemy Model  → Describes the DATABASE TABLE
#   schemas.py → Pydantic Schema   → Describes the API INPUT/OUTPUT
#
# WHY TWO DIFFERENT THINGS?
#   Because what the DATABASE stores and what the API accepts/returns
#   are often different:
#
#   - The DB has 'created_at' and 'id' (auto-generated) — we don't
#     want users sending these in a POST request
#   - The API might return a computed field like 'interview_count'
#     that isn't stored in the DB
#   - Pydantic automatically validates types and required fields,
#     returning clear 422 errors if input is wrong
#
# REQUEST FLOW:
#   POST /applications  →  JSON body  →  Pydantic validates  →  SQLAlchemy saves
#   GET  /applications  →  SQLAlchemy reads  →  Pydantic formats  →  JSON response
# ============================================================

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from models import ApplicationStatus, InterviewType, InterviewOutcome


# ──────────────────────────────────────────────
# INTERVIEW ROUND SCHEMAS
# ──────────────────────────────────────────────

class InterviewRoundBase(BaseModel):
    """Fields shared by create and read operations."""
    round_number:   int          = Field(default=1, ge=1, description="Round sequence number (1, 2, 3...)")
    interview_type: InterviewType
    scheduled_at:   Optional[datetime] = None
    outcome:        InterviewOutcome    = InterviewOutcome.PENDING
    interviewer:    Optional[str]       = Field(None, max_length=200)
    notes:          Optional[str]       = None


class InterviewRoundCreate(InterviewRoundBase):
    """Schema for creating a new interview round (POST request body)."""
    pass  # inherits all fields from InterviewRoundBase


class InterviewRoundResponse(InterviewRoundBase):
    """Schema for returning an interview round in API responses."""
    id:             int
    application_id: int
    created_at:     datetime

    class Config:
        # orm_mode = True (Pydantic v1) → from_orm=True in Pydantic v2
        # Tells Pydantic to read data from SQLAlchemy model attributes
        # Without this, Pydantic can't read SQLAlchemy model objects
        from_attributes = True


# ──────────────────────────────────────────────
# APPLICATION SCHEMAS
# ──────────────────────────────────────────────

class ApplicationBase(BaseModel):
    """
    Fields shared by Create, Update, and Response schemas.
    These are the fields all operations share.
    """
    company_name:  str  = Field(..., min_length=1, max_length=200, description="Company name")
    role:          str  = Field(..., min_length=1, max_length=200, description="Job title or role")
    location:      Optional[str] = Field(None, max_length=200, description="City, Remote, Hybrid...")
    source:        Optional[str] = Field(None, max_length=100, description="LinkedIn, Indeed, Referral...")
    status:        ApplicationStatus = ApplicationStatus.APPLIED
    applied_date:  Optional[date]    = None
    salary_range:  Optional[str]     = Field(None, max_length=100, description="e.g. 10-15 LPA")
    notes:         Optional[str]     = None
    job_url:       Optional[str]     = Field(None, max_length=500)

    # Field(...) means REQUIRED — no default value
    # Field(None, ...) means OPTIONAL — defaults to None


class ApplicationCreate(ApplicationBase):
    """
    Schema for creating a new application.
    Used in: POST /applications

    The user sends this JSON:
    {
        "company_name": "Google",
        "role": "Software Engineer",
        "location": "Bangalore",
        "source": "LinkedIn",
        "status": "Applied"
    }
    """
    pass  # All fields inherited from ApplicationBase


class ApplicationUpdate(BaseModel):
    """
    Schema for updating an existing application.
    Used in: PATCH /applications/{id}

    ALL fields are optional here because PATCH means
    'update only the fields I provide'.

    Example: only update the status:
    { "status": "Interview" }
    """
    company_name:  Optional[str]              = Field(None, min_length=1, max_length=200)
    role:          Optional[str]              = Field(None, min_length=1, max_length=200)
    location:      Optional[str]              = Field(None, max_length=200)
    source:        Optional[str]              = Field(None, max_length=100)
    status:        Optional[ApplicationStatus] = None
    applied_date:  Optional[date]             = None
    salary_range:  Optional[str]              = Field(None, max_length=100)
    notes:         Optional[str]              = None
    job_url:       Optional[str]              = Field(None, max_length=500)


class ApplicationResponse(ApplicationBase):
    """
    Schema for returning application data in API responses.
    Used in: GET /applications, GET /applications/{id}, POST /applications, etc.

    Includes auto-generated fields (id, created_at, updated_at)
    and the related interview rounds.
    """
    id:               int
    created_at:       datetime
    updated_at:       datetime
    interview_rounds: List[InterviewRoundResponse] = []

    class Config:
        from_attributes = True  # Required to read from SQLAlchemy model objects


class ApplicationSummary(BaseModel):
    """
    Lightweight version of ApplicationResponse without interview_rounds.
    Used in list endpoints to avoid loading all nested data.
    """
    id:           int
    company_name: str
    role:         str
    location:     Optional[str]
    source:       Optional[str]
    status:       ApplicationStatus
    applied_date: Optional[date]
    created_at:   datetime
    updated_at:   datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
# DASHBOARD / ANALYTICS SCHEMAS
# ──────────────────────────────────────────────

class StatusCount(BaseModel):
    """Count of applications per status."""
    status: str
    count:  int


class DashboardResponse(BaseModel):
    """
    Analytics summary returned by GET /dashboard.
    This is a COMPUTED response — not directly from a single table.
    """
    total_applications:     int
    active_applications:    int   # Not Rejected and not Withdrawn
    status_breakdown:       List[StatusCount]
    recent_applications:    List[ApplicationSummary]
    applications_this_week: int
    offers_received:        int
    rejection_rate:         float  # percentage 0.0 to 100.0


# ──────────────────────────────────────────────
# GENERIC RESPONSE SCHEMAS
# ──────────────────────────────────────────────

class MessageResponse(BaseModel):
    """Simple success/info message response."""
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status:  str
    service: str
    version: str
