"""
=============================================================
  app/services/ai_service.py — AI Service Layer
=============================================================

📌 WHAT IS THIS FILE?
  This is the service layer that orchestrates AI operations. 
  It acts as the middleman between the controller (HTTP layer) and 
  the Gemini utility client.

📌 RESPONSIBILITIES:
  1. Fetch a report from PostgreSQL by ID.
  2. Verify that the report contains extracted text.
  3. Orchestrate Gemini API requests for clinical summary and patient explanation.
  4. Persist the generated AI outputs back to the database.
  5. Manage and transition the report's processing status.
"""

import logging
from sqlalchemy.orm import Session
from app.models.report import Report, ReportStatus
from app.utils.gemini_client import (
    generate_clinical_summaries,
    generate_patient_explanations,
    GeminiAPIError,
)

# Configure professional logger
logger = logging.getLogger("ai_service")


class ReportNotFoundError(Exception):
    """Raised when a requested report does not exist in the database."""
    pass


class EmptyReportTextError(Exception):
    """Raised when a report exists but has no extracted text to summarize."""
    pass


class AIService:
    """
    Service class handling all business logic for AI Summarization.
    """

    def summarize_report(self, db: Session, report_id: int) -> Report:
        """
        Orchestrate the full AI summarization pipeline for a specific report.

        📌 LIFECYCLE FLOW:
        1. Find report in DB. (Raise ReportNotFoundError if missing).
        2. Validate extracted_text. (Raise EmptyReportTextError if empty).
        3. Transition status to 'processing' and commit.
        4. Query Gemini to generate clinical summary.
        5. Query Gemini to generate patient-friendly explanation.
        6. Update 'ai_summary' and 'patient_explanation' in DB.
        7. Transition status to 'completed' and commit.
        8. If any API failure happens, transition status to 'failed' and commit.

        Args:
            db: Database session.
            report_id: The ID of the report to process.

        Returns:
            Report: The updated, persistent Report SQLAlchemy object.

        Raises:
            ReportNotFoundError: If report not found.
            EmptyReportTextError: If report has no extracted text.
            GeminiAPIError: If external AI calls fail.
        """
        # Step 1: Find the report
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            error_msg = f"Report with ID {report_id} not found."
            logger.error(error_msg)
            raise ReportNotFoundError(error_msg)

        # Step 2: Validate that extracted text exists
        if not report.extracted_text or not report.extracted_text.strip():
            # If the report is pending or was an image with no text yet
            error_msg = f"Report with ID {report_id} has no extracted text to summarize."
            logger.warning(error_msg)
            
            # Update status to failed since we cannot process it
            report.status = ReportStatus.FAILED
            db.commit()
            db.refresh(report)
            raise EmptyReportTextError(error_msg)

        # Step 3: Set status to 'processing' to lock the resource and commit immediately
        logger.info(f"Report ID {report_id} found. Setting status to 'processing'...")
        report.status = ReportStatus.PROCESSING
        db.commit()
        db.refresh(report)

        try:
            # Step 4: Generate clinical summary (English and Hindi)
            clinical_summary, hindi_summary = generate_clinical_summaries(report.extracted_text)
            logger.info(f"AI summary (English) generated successfully for Report ID {report_id} (Length: {len(clinical_summary)} characters).")
            logger.info(f"AI summary (Hindi) generated successfully for Report ID {report_id} (Length: {len(hindi_summary)} characters).")

            # Step 5: Generate patient explanation (English and Hindi)
            patient_explanation, hindi_explanation = generate_patient_explanations(report.extracted_text)
            logger.info(f"Patient explanation (English) generated successfully for Report ID {report_id} (Length: {len(patient_explanation)} characters).")
            logger.info(f"Patient explanation (Hindi) generated successfully for Report ID {report_id} (Length: {len(hindi_explanation)} characters).")

            # Step 6: Save results and transition to 'completed'
            report.ai_summary = clinical_summary
            report.hindi_summary = hindi_summary
            report.patient_explanation = patient_explanation
            report.hindi_explanation = hindi_explanation
            report.status = ReportStatus.COMPLETED
            
            db.commit()
            db.refresh(report)
            logger.info(f"Successfully saved AI summary (English/Hindi), and Patient explanation (English/Hindi) to database for Report ID {report_id}.")
            return report

        except GeminiAPIError as e:
            # Step 7: Handle API failures gracefully - set status to failed
            logger.error(f"AI Summarization failed for Report ID {report_id} due to API Error: {str(e)}")
            
            report.status = ReportStatus.FAILED
            db.commit()
            db.refresh(report)
            
            # Re-raise the exception to allow the controller to map it to a proper HTTP status code
            raise
            
        except Exception as e:
            # General unexpected error fallback
            logger.error(f"Unexpected error in AI service for Report ID {report_id}: {str(e)}", exc_info=True)
            
            report.status = ReportStatus.FAILED
            db.commit()
            db.refresh(report)
            raise GeminiAPIError(f"Unexpected summarization error: {str(e)}")


# ──────────────────────────────────────────────
# SINGLETON INSTANCE
# ──────────────────────────────────────────────
ai_service = AIService()
