# ============================================================
# models.py
# SQLAlchemy ORM models — defines the database tables as Python classes.
#
# WHAT IS AN ORM MODEL?
#   Each class here maps to one table in PostgreSQL.
#   Each class attribute maps to one column in that table.
#   SQLAlchemy reads these classes and knows how to:
#     - CREATE the tables
#     - INSERT rows
#     - SELECT rows
#     - UPDATE rows
#     - DELETE rows
#   ...all without writing raw SQL.
#
# OUR TWO TABLES:
#   applications  → stores each job application
#   interview_rounds → stores interview rounds for each application
# ============================================================

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum as SAEnum, Date
)
from sqlalchemy.orm import relationship
from database import Base


# ──────────────────────────────────────────────
# ENUMS
# An Enum is a fixed set of allowed values.
# We use Enums for status fields to prevent
# invalid data like status="dunno" being stored.
# ──────────────────────────────────────────────

class ApplicationStatus(str, enum.Enum):
    """
    The possible stages of a job application.
    Using str makes it JSON-serializable automatically.
    """
    APPLIED    = "Applied"
    SCREENING  = "Screening"
    INTERVIEW  = "Interview"
    OFFER      = "Offer"
    REJECTED   = "Rejected"
    WITHDRAWN  = "Withdrawn"


class InterviewType(str, enum.Enum):
    """Types of interview rounds."""
    PHONE      = "Phone"
    TECHNICAL  = "Technical"
    HR         = "HR"
    ASSIGNMENT = "Assignment"
    FINAL      = "Final"
    OTHER      = "Other"


class InterviewOutcome(str, enum.Enum):
    """Outcome of an interview round."""
    PENDING    = "Pending"
    PASSED     = "Passed"
    FAILED     = "Failed"


# ──────────────────────────────────────────────
# TABLE 1: applications
# ──────────────────────────────────────────────

class Application(Base):
    """
    Represents one job application.

    TABLE COLUMNS:
    ┌─────────────────┬────────────────┬─────────────────────────────────┐
    │ Column          │ Type           │ Description                     │
    ├─────────────────┼────────────────┼─────────────────────────────────┤
    │ id              │ Integer (PK)   │ Auto-incrementing unique ID      │
    │ company_name    │ String(200)    │ Company name (required)         │
    │ role            │ String(200)    │ Job title / role (required)     │
    │ location        │ String(200)    │ City, remote, hybrid (optional) │
    │ source          │ String(100)    │ LinkedIn, Indeed, Referral...   │
    │ status          │ Enum           │ Current application stage       │
    │ applied_date    │ Date           │ Date of application             │
    │ salary_range    │ String(100)    │ e.g. "10-15 LPA" (optional)     │
    │ notes           │ Text           │ Free-form notes (optional)      │
    │ job_url         │ String(500)    │ URL to the job listing          │
    │ created_at      │ DateTime       │ Auto-set when record is created │
    │ updated_at      │ DateTime       │ Auto-updated on every change    │
    └─────────────────┴────────────────┴─────────────────────────────────┘
    """
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    # index=True on primary key creates a database index for fast lookups

    company_name  = Column(String(200), nullable=False)
    # nullable=False means this field is REQUIRED — PostgreSQL will reject empty values

    role          = Column(String(200), nullable=False)
    location      = Column(String(200), nullable=True)
    source        = Column(String(100), nullable=True)

    status = Column(
        SAEnum(ApplicationStatus, name="applicationstatus"),
        nullable=False,
        default=ApplicationStatus.APPLIED
    )
    # SAEnum creates a PostgreSQL ENUM type with these exact allowed values

    applied_date  = Column(Date, nullable=True)
    salary_range  = Column(String(100), nullable=True)
    notes         = Column(Text, nullable=True)
    job_url       = Column(String(500), nullable=True)

    # Audit timestamps — automatically managed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    # onupdate=datetime.utcnow → SQLAlchemy updates this column automatically on every UPDATE

    # RELATIONSHIP: one Application has many InterviewRounds
    # cascade="all, delete-orphan" → if we delete an application,
    # its interview rounds are automatically deleted too
    interview_rounds = relationship(
        "InterviewRound",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """String representation for debugging."""
        return f"<Application(id={self.id}, company='{self.company_name}', role='{self.role}', status='{self.status}')>"


# ──────────────────────────────────────────────
# TABLE 2: interview_rounds
# ──────────────────────────────────────────────

class InterviewRound(Base):
    """
    Represents one interview round for a job application.
    A single application can have multiple rounds (Phone → Technical → HR → Final).

    TABLE COLUMNS:
    ┌──────────────────┬──────────────┬──────────────────────────────────┐
    │ Column           │ Type         │ Description                      │
    ├──────────────────┼──────────────┼──────────────────────────────────┤
    │ id               │ Integer (PK) │ Auto-incrementing unique ID       │
    │ application_id   │ Integer (FK) │ Links to applications.id         │
    │ round_number     │ Integer      │ 1, 2, 3... (round sequence)      │
    │ interview_type   │ Enum         │ Phone, Technical, HR, etc.       │
    │ scheduled_at     │ DateTime     │ When the interview is scheduled  │
    │ outcome          │ Enum         │ Pending / Passed / Failed        │
    │ interviewer      │ String(200)  │ Interviewer name (optional)      │
    │ notes            │ Text         │ Notes about the round            │
    │ created_at       │ DateTime     │ Auto-set on creation             │
    └──────────────────┴──────────────┴──────────────────────────────────┘
    """
    __tablename__ = "interview_rounds"

    id             = Column(Integer, primary_key=True, index=True)

    # FOREIGN KEY: links each interview round to its parent application
    # ondelete="CASCADE" → if the application is deleted, rounds are deleted too (DB level)
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # index for fast lookups by application_id
    )

    round_number   = Column(Integer, nullable=False, default=1)
    interview_type = Column(SAEnum(InterviewType, name="interviewtype"), nullable=False)
    scheduled_at   = Column(DateTime, nullable=True)
    outcome        = Column(
        SAEnum(InterviewOutcome, name="interviewoutcome"),
        nullable=False,
        default=InterviewOutcome.PENDING
    )
    interviewer    = Column(String(200), nullable=True)
    notes          = Column(Text, nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Back-reference to the parent Application
    application = relationship("Application", back_populates="interview_rounds")

    def __repr__(self):
        return f"<InterviewRound(id={self.id}, app_id={self.application_id}, type='{self.interview_type}', outcome='{self.outcome}')>"
