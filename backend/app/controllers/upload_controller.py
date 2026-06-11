"""
=============================================================
  app/controllers/upload_controller.py — Upload Controller
=============================================================

📌 WHAT IS THIS FILE?
  The Controller layer for file uploads.
  It sits between the Route and the Service:
  
  HTTP Request (multipart/form-data with a file)
      ↓
  Route (routes/upload.py)
    → Receives the UploadFile + report_id
      ↓
  Controller (controllers/upload_controller.py)   ← THIS FILE
    → Validates report_id, calls the upload service, maps errors to HTTP
      ↓
  Service (services/upload_service.py)
    → Validates file, saves to disk, updates DB
      ↓
  Database (models/report.py)
    → Stores file metadata in the reports table

📌 CONTROLLER vs SERVICE REMINDER:
  Controller → "What HTTP status code should I return?"
  Service    → "How do I actually save this file and validate it?"
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.services.upload_service import upload_service


class UploadController:
    """
    Controller for file upload operations.
    
    Orchestrates the upload workflow and translates
    service-level results into HTTP-appropriate responses.
    """

    def upload_file(self, db: Session, report_id: int, file: UploadFile) -> dict:
        """
        Handle a file upload request.
        
        📌 WHAT THIS METHOD DOES:
        1. Validates that report_id is a positive integer
        2. Delegates to upload_service.process_upload()
        3. If the service returns an error, raises the appropriate HTTPException
        4. If successful, returns the upload result
        
        📌 WHY VALIDATE report_id HERE?
        The route already ensures report_id is an int (via path parameter typing).
        But we add an extra check for positive values — this is a controller
        concern because it relates to HTTP request validation.
        
        Args:
            db: Database session (injected by FastAPI in the route)
            report_id: ID of the report to attach the file to
            file: The uploaded file from the HTTP request
        
        Returns:
            dict with upload success info
        
        Raises:
            HTTPException 400: If report_id is invalid or file validation fails
            HTTPException 404: If the report doesn't exist
            HTTPException 500: If an unexpected error occurs during upload
        """

        # --- Validate report_id ---
        if report_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report ID must be a positive integer."
            )

        # --- Delegate to the upload service ---
        try:
            result = upload_service.process_upload(
                db=db,
                report_id=report_id,
                file=file,
            )
        except Exception as e:
            # Catch any unexpected errors (disk full, permission denied, etc.)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during file upload: {str(e)}"
            )

        # --- Map service result to HTTP response ---
        if not result["success"]:
            error_msg = result["error"]

            # Determine the right HTTP status code based on the error
            if "not found" in error_msg.lower():
                # Report doesn't exist → 404
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error_msg,
                )
            else:
                # Validation error (wrong type, too large, etc.) → 400
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg,
                )

        # Success! Return the result dict directly.
        # The route will serialize this as JSON.
        return result


# ──────────────────────────────────────────────
# SINGLETON INSTANCE
# ──────────────────────────────────────────────

"""
📌 Same singleton pattern as ReportController.

Usage in routes:
    from app.controllers.upload_controller import upload_controller
    result = upload_controller.upload_file(db, report_id, file)
"""

upload_controller = UploadController()
