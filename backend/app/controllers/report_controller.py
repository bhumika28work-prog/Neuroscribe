"""
=============================================================
  app/controllers/report_controller.py — Controller Layer
=============================================================

📌 WHAT IS A CONTROLLER?
  The Controller sits between Routes and Services.
  
  CLEAN ARCHITECTURE FLOW:
  
  HTTP Request
      ↓
  Route (routes/reports.py)
    → Handles HTTP: reads request data, sets HTTP status codes
      ↓
  Controller (controllers/report_controller.py)
    → Orchestrates: calls services, handles errors, prepares responses
      ↓
  Service (services/report_service.py)
    → Business logic: validation, transformations, DB operations
      ↓
  Model (models/report.py)
    → Database: CRUD operations via SQLAlchemy

📌 ROUTE vs CONTROLLER vs SERVICE:
  Route      → "What HTTP endpoint is this? What's the URL?"
  Controller → "What happens when this endpoint is called?"
  Service    → "How do we actually DO the thing?"
  
  Example:
    Route:      @router.get("/reports/{id}")
    Controller: validate id > 0, call service, handle 404
    Service:    db.query(Report).filter(Report.id == id).first()

📌 WHY THIS SEPARATION?
  In small projects, you might merge Controller + Service.
  In large projects, this separation means:
  ✅ Controllers handle only request/response orchestration
  ✅ Services handle only pure business logic
  ✅ Easy to test each layer independently
  ✅ Easy to swap implementations (e.g., different DB)

📌 NOTE FOR BEGINNERS:
  Some FastAPI tutorials skip the controller layer and put
  logic directly in routes or services. That's fine for small
  apps. We include it here to show you industry-standard
  clean architecture from the start.
"""

import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.report_service import report_service
from app.schemas.report import ReportUpdate

logger = logging.getLogger("report_controller")


class ReportController:
    """
    Controller for report-related operations.
    Orchestrates service calls and handles HTTP-level concerns
    like status codes and error responses.
    """

    def get_all(self, db: Session, page: int = 1, per_page: int = 10):
        """
        Get paginated list of reports.
        
        📌 PAGINATION CALCULATION:
          page=1, per_page=10 → skip=0,  limit=10
          page=2, per_page=10 → skip=10, limit=10
          page=3, per_page=10 → skip=20, limit=10
        
        Args:
            db: Database session (injected by FastAPI)
            page: Page number (1-indexed)
            per_page: Number of items per page
        
        Returns:
            dict with pagination info and list of reports
        """
        # Validate inputs
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be 1 or greater"
            )
        if per_page < 1 or per_page > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="per_page must be between 1 and 100"
            )

        # Calculate skip offset for pagination
        skip = (page - 1) * per_page

        # Call the service to get data
        reports = report_service.get_all_reports(db=db, skip=skip, limit=per_page)

        return {
            "total": len(reports),
            "page": page,
            "per_page": per_page,
            "reports": reports
        }

    def get_by_id(self, db: Session, report_id: int):
        """
        Get a single report by ID.
        
        📌 HTTP 404 NOT FOUND:
          If the report doesn't exist, we raise an HTTPException
          with status 404. FastAPI converts this to a proper
          HTTP 404 response with the detail message.
        
        Args:
            db: Database session
            report_id: The ID to look up
        
        Returns:
            Report object
        
        Raises:
            HTTPException 404: If report not found
            HTTPException 400: If report_id is invalid
        """
        if report_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID must be a positive integer"
            )

        report = report_service.get_report_by_id(db=db, report_id=report_id)

        if not report:
            # 📌 Raise 404 if not found — FastAPI converts to JSON error response
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found"
            )

        logger.info(
            f"API returning Report ID {report_id} "
            f"(Has summary (English): {report.ai_summary is not None}, "
            f"Has summary (Hindi): {report.hindi_summary is not None}, "
            f"Has English patient explanation: {report.patient_explanation is not None}, "
            f"Has Hindi patient explanation: {report.hindi_explanation is not None})"
        )
        return report

    def create(self, db: Session, report_data):
        """
        Create a new report.
        
        📌 HTTP STATUS CODES:
          200 OK         → Generic success
          201 Created    → New resource was created (use for POST)
          400 Bad Request → Client sent invalid data
          422 Unprocessable → Pydantic validation failed (automatic)
          500 Server Error → Something went wrong on our side
        
        Args:
            db: Database session
            report_data: Validated ReportCreate Pydantic schema
        
        Returns:
            Newly created report
        """
        try:
            new_report = report_service.create_report(db=db, report_data=report_data)
            return new_report
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create report: {str(e)}"
            )

    def update(self, db: Session, report_id: int, report_data: ReportUpdate):
        """
        Update an existing report.

        Args:
            db: Database session
            report_id: ID of the report to update
            report_data: Pydantic ReportUpdate (partial fields allowed)

        Returns:
            Updated Report object

        Raises:
            HTTPException 404: If report not found
        """
        updated = report_service.update_report(db=db, report_id=report_id, report_data=report_data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found"
            )
        return updated

    def delete(self, db: Session, report_id: int):
        """
        Delete a report by ID.

        Args:
            db: Database session
            report_id: ID of report to delete

        Returns:
            Success message

        Raises:
            HTTPException 404: If report not found
        """
        deleted = report_service.delete_report(db=db, report_id=report_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found"
            )

        return {"success": True, "message": f"Report {report_id} deleted successfully"}


# ── Singleton instance ──
report_controller = ReportController()
