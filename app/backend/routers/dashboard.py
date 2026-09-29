# ============================================================
# routers/dashboard.py
# Analytics and dashboard data endpoints.
#
# These endpoints aggregate data from the applications table
# and return computed statistics for the frontend dashboard.
# ============================================================

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/",
    response_model=schemas.DashboardResponse,
    summary="Get dashboard analytics summary"
)
def get_dashboard(db: Session = Depends(get_db)):
    """
    Returns aggregated statistics for the dashboard.

    Computes:
    - Total applications
    - Active applications (not rejected/withdrawn)
    - Status breakdown (count per status)
    - Last 5 recent applications
    - Applications submitted this week
    - Total offers received
    - Rejection rate percentage
    """
    # Total count of all applications
    total = db.query(func.count(models.Application.id)).scalar() or 0

    # Active = not Rejected and not Withdrawn
    active = db.query(func.count(models.Application.id)).filter(
        models.Application.status.notin_([
            models.ApplicationStatus.REJECTED,
            models.ApplicationStatus.WITHDRAWN
        ])
    ).scalar() or 0

    # Count per status — using GROUP BY
    # Result: [("Applied", 5), ("Interview", 3), ...]
    status_rows = (
        db.query(models.Application.status, func.count(models.Application.id))
        .group_by(models.Application.status)
        .all()
    )
    status_breakdown = [
        schemas.StatusCount(status=row[0].value, count=row[1])
        for row in status_rows
    ]

    # 5 most recently updated applications
    recent = (
        db.query(models.Application)
        .order_by(models.Application.updated_at.desc())
        .limit(5)
        .all()
    )

    # Applications submitted in the last 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = db.query(func.count(models.Application.id)).filter(
        models.Application.created_at >= one_week_ago
    ).scalar() or 0

    # Total offers
    offers = db.query(func.count(models.Application.id)).filter(
        models.Application.status == models.ApplicationStatus.OFFER
    ).scalar() or 0

    # Rejection rate = (rejected / total) * 100
    rejected = db.query(func.count(models.Application.id)).filter(
        models.Application.status == models.ApplicationStatus.REJECTED
    ).scalar() or 0

    rejection_rate = round((rejected / total * 100), 1) if total > 0 else 0.0

    return schemas.DashboardResponse(
        total_applications=total,
        active_applications=active,
        status_breakdown=status_breakdown,
        recent_applications=recent,
        applications_this_week=this_week,
        offers_received=offers,
        rejection_rate=rejection_rate,
    )
