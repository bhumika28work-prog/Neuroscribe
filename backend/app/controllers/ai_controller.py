"""
=============================================================
  app/controllers/ai_controller.py — AI Controller Layer
=============================================================

📌 WHAT IS THIS FILE?
  The Controller layer sits between the Route and the Service.
  It is responsible for:
  1. Validating request parameters.
  2. Orchestrating service calls.
  3. Catching service-level errors and raising HTTP-level exceptions 
     with proper status codes.
"""

import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.services.ai_service import (
    ai_service,
    ReportNotFoundError,
    EmptyReportTextError,
    GeminiAPIError,
)

# Standard logger configuration
logger = logging.getLogger("ai_controller")


class AIController:
    """
    Controller for AI-related operations.
    Translates business logic results and errors into HTTP responses.
    """

    def summarize(self, db: Session, report_id: int) -> dict:
        """
        Handle a request to trigger AI summarization.

        📌 HTTP MAPPING:
        - ReportNotFoundError ➔ 404 Not Found
        - EmptyReportTextError ➔ 400 Bad Request
        - GeminiAPIError ➔ 502 Bad Gateway (upstream API failed)
        - Generic Exception ➔ 500 Internal Server Error

        Args:
            db: Database session.
            report_id: The ID of the report to summarize.

        Returns:
            dict: The updated report serialization response or success details.
        
        Raises:
            HTTPException: Corresponding HTTP status code and detail.
        """
        # Request-level validation
        if report_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID must be a positive integer."
            )

        try:
            logger.info(f"AI Controller received request to summarize report ID {report_id}")
            report = ai_service.summarize_report(db=db, report_id=report_id)
            return report

        except ReportNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )

        except EmptyReportTextError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        except GeminiAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External AI Provider Error: {str(e)}"
            )

        except Exception as e:
            logger.error(f"Unexpected controller error for report {report_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )


# ──────────────────────────────────────────────
# SINGLETON INSTANCE
# ──────────────────────────────────────────────
ai_controller = AIController()
