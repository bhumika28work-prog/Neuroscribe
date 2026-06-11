"""
=============================================================
  app/routes/report.py — FastAPI Router for Report CRUD
=============================================================
"""

# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Import the DB dependency that yields a session
from app.database.connection import get_db

# Import Pydantic schemas for request validation and response models
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
)

# Import the controller that contains the business‑logic orchestration
from app.controllers.report_controller import report_controller
from app.controllers.ai_controller import ai_controller

# ------------------------------------------------------------
# CREATE ROUTER
# ------------------------------------------------------------
router = APIRouter()

# ------------------------------------------------------------
# ENDPOINT: Create a new report (POST /reports)
# ------------------------------------------------------------
@router.post(
    "/reports",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical report",
    description="Accepts a ReportCreate payload and returns the created report with its generated ID and timestamps.",
)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new report.

    FastAPI automatically validates `report` against the `ReportCreate` schema.
    The controller handles the actual DB insertion and returns a SQLAlchemy model
    which FastAPI serialises into the `ReportResponse` schema.
    """
    created = report_controller.create(db=db, report_data=report)
    return created

# ------------------------------------------------------------
# ENDPOINT: Get paginated list of reports (GET /reports)
# ------------------------------------------------------------
@router.get(
    "/reports",
    response_model=ReportListResponse,
    summary="List reports (paginated)",
    description="Returns a page of reports together with pagination metadata.",
)
def list_reports(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    """Retrieve a paginated list of reports.

    * `page` – 1‑based page number (default 1).
    * `per_page` – how many items per page (default 10, max 100).
    """
    return report_controller.get_all(db=db, page=page, per_page=per_page)

# ------------------------------------------------------------
# ENDPOINT: Get a single report by ID (GET /reports/{id})
# ------------------------------------------------------------
@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    summary="Get a single report",
    description="Fetch a report by its unique identifier. Returns 404 if not found.",
)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Fetch a report by ID.

    The `report_id` path parameter is validated as an integer by FastAPI.
    """
    return report_controller.get_by_id(db=db, report_id=report_id)

# ------------------------------------------------------------
# ENDPOINT: Update a report (PUT /reports/{id})
# ------------------------------------------------------------
@router.put(
    "/reports/{report_id}",
    response_model=ReportResponse,
    summary="Update a report",
    description="Replace an existing report's mutable fields. Returns the updated report.",
)
def update_report(report_id: int, report: ReportUpdate, db: Session = Depends(get_db)):
    """Update a report.

    FastAPI validates the payload against `ReportUpdate` where all fields are optional.
    The controller delegates the update logic to the service layer.
    """
    return report_controller.update(db=db, report_id=report_id, report_data=report)

# ------------------------------------------------------------
# ENDPOINT: Delete a report (DELETE /reports/{id})
# ------------------------------------------------------------
@router.delete(
    "/reports/{report_id}",
    summary="Delete a report",
    description="Delete a report by its ID. Returns a simple success message.",
)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report by ID.

    Returns a JSON body with `success: true` and a message.
    """
    return report_controller.delete(db=db, report_id=report_id)


# ------------------------------------------------------------
# ENDPOINT: Trigger AI Summarization on-demand (POST /reports/{id}/summarize)
# ------------------------------------------------------------
@router.post(
    "/reports/{report_id}/summarize",
    response_model=ReportResponse,
    summary="Trigger AI summarization for a report",
    description="Analyzes the report's extracted text using Google Gemini to generate clinical summaries and patient explanations.",
)
def summarize_report(report_id: int, db: Session = Depends(get_db)):
    """Trigger AI summarization on-demand.

    Requires the report to already have extracted_text (e.g. from a successful PDF upload).
    """
    return ai_controller.summarize(db=db, report_id=report_id)

