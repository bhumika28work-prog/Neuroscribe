"""
=============================================================
  app/services/upload_service.py — File Upload Business Logic
=============================================================

📌 WHAT IS THIS FILE?
  This is the SERVICE layer for file uploads.
  It handles ALL the business logic related to uploading files:
  
  1. Validating file type (PDF, JPG, PNG only)
  2. Validating file size (max 10 MB by default)
  3. Generating unique filenames (to prevent collisions)
  4. Saving files to the local filesystem
  5. Updating the Report record in the database with file info

📌 WHY A SEPARATE UPLOAD SERVICE?
  The Report Service handles CRUD on report records.
  The Upload Service handles file-specific logic.
  
  This keeps responsibilities clear:
  ┌──────────────────────────┐
  │  ReportService           │  → Create, Read, Update, Delete reports
  ├──────────────────────────┤
  │  UploadService           │  → Validate files, save to disk, link to report
  └──────────────────────────┘
  
  Later you'll add an OCRService, AISummaryService, etc.

📌 HOW FILE UPLOADS WORK IN WEB APPS:
  1. Client sends a file via HTTP POST (multipart/form-data)
  2. FastAPI receives it as an UploadFile object (in-memory or temp file)
  3. Your code validates the file (type, size)
  4. Your code saves the file to a permanent location on disk
  5. The file path is stored in the database
  6. Later, other services (OCR, AI) can read the file from that path

📌 WHAT IS multipart/form-data?
  Normal JSON requests look like:
    {"title": "Blood Test", "content": "..."}
  
  But files are BINARY data (not text), so they can't be sent as JSON.
  Instead, browsers use "multipart/form-data" encoding which:
  - Splits the request body into multiple "parts"
  - Each part can be text OR binary
  - This is the same format used by HTML <form> with <input type="file">
  
  FastAPI handles this automatically when you use UploadFile.
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

import os          # For filesystem operations (mkdir, path joins)
import uuid        # For generating unique filenames
import shutil      # For copying file data from memory to disk
import logging     # For professional activity logging
from pathlib import Path  # Modern, cross-platform file path handling
from datetime import datetime  # For organizing uploads into date folders

from fastapi import UploadFile  # FastAPI's file upload type
from sqlalchemy.orm import Session  # Database session type

# Our own modules
from app.core.config import settings   # App settings (max size, allowed types)
from app.models.report import Report, ReportStatus   # The Report ORM model and status Enum
from app.utils.pdf_extractor import extract_text_from_pdf, PDFExtractionError
from app.services.ai_service import ai_service

# Configure logger for the service
logger = logging.getLogger("upload_service")



# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────

"""
📌 UPLOAD DIRECTORY:
  We store uploaded files in a folder called "uploads" inside the
  backend directory. This keeps files organized and separate from code.
  
  Structure:
    backend/
      uploads/
        2025/
          05/
            abc123_blood_test.pdf
            def456_xray.png

📌 WHY ORGANIZE BY DATE?
  As your app grows, you might have thousands of files.
  Organizing by year/month makes it easier to:
  - Find files manually
  - Archive old files
  - Set up backup schedules
"""

# Base directory for all uploads — relative to the project root
UPLOAD_DIR = Path("uploads")

# Convert max upload size from MB to bytes for comparison
# Example: 10 MB × 1024 KB/MB × 1024 bytes/KB = 10,485,760 bytes
MAX_FILE_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Allowed MIME types mapped from file extensions
# We check BOTH the extension AND the MIME type for security
ALLOWED_MIME_TYPES = {
    "application/pdf",           # PDF documents
    "image/jpeg",                # JPG / JPEG images
    "image/png",                 # PNG images
}

# Allowed file extensions (lowercase, without the dot)
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}


class UploadService:
    """
    Service class for handling file upload operations.
    
    📌 RESPONSIBILITIES:
    1. validate_file()       → Check type and size before saving
    2. generate_filename()   → Create a unique name to prevent collisions
    3. save_file()           → Write the file to the local filesystem
    4. process_upload()      → Orchestrate the full upload workflow
    """

    # ──────────────────────────────────────────
    # 1. FILE VALIDATION
    # ──────────────────────────────────────────

    def validate_file(self, file: UploadFile) -> dict:
        """
        Validate an uploaded file before saving it.
        
        📌 WHAT WE CHECK:
        1. File is not empty (has a filename)
        2. File extension is in our allowed list
        3. MIME type matches expected types
        4. File size doesn't exceed the maximum
        
        📌 WHY VALIDATE?
        Security! Without validation, someone could upload:
        - A .exe virus disguised as a PDF
        - A 10 GB file that fills your disk
        - A script that exploits your server
        
        Always validate BOTH the extension AND the MIME type.
        Extensions can be faked, but checking both adds a layer of safety.
        
        Args:
            file: FastAPI's UploadFile object
        
        Returns:
            dict with "valid" (bool) and "error" (str or None)
        """
        
        # --- Check 1: File must have a name ---
        if not file.filename:
            return {
                "valid": False,
                "error": "No filename provided. Please select a file to upload."
            }

        # --- Check 2: Extract and validate the file extension ---
        # "blood_test.pdf" → extension = "pdf"
        # We use os.path.splitext to safely split filename and extension
        _, extension = os.path.splitext(file.filename)
        
        # Remove the dot and convert to lowercase: ".PDF" → "pdf"
        extension = extension.lstrip(".").lower()

        if extension not in ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": (
                    f"File type '.{extension}' is not allowed. "
                    f"Supported types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
                )
            }

        # --- Check 3: Validate MIME type ---
        # MIME type is set by the browser based on file content
        # Example: "application/pdf", "image/jpeg"
        if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
            return {
                "valid": False,
                "error": (
                    f"MIME type '{file.content_type}' is not allowed. "
                    f"Expected one of: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
                )
            }

        # --- Check 4: Validate file size ---
        # We read the entire file into memory to check its size.
        # file.file is the underlying SpooledTemporaryFile from Python's
        # tempfile module.  We seek to the end, get the position (= size),
        # then seek back to the start so the file can still be read later.
        file.file.seek(0, 2)          # Seek to end of file
        file_size = file.file.tell()  # Current position = file size in bytes
        file.file.seek(0)             # Seek back to start (IMPORTANT!)

        if file_size == 0:
            return {
                "valid": False,
                "error": "The uploaded file is empty (0 bytes)."
            }

        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = round(file_size / (1024 * 1024), 2)
            return {
                "valid": False,
                "error": (
                    f"File size ({size_mb} MB) exceeds the maximum "
                    f"allowed size ({settings.MAX_UPLOAD_SIZE_MB} MB)."
                )
            }

        # All checks passed!
        return {"valid": True, "error": None, "file_size": file_size, "extension": extension}

    # ──────────────────────────────────────────
    # 2. UNIQUE FILENAME GENERATION
    # ──────────────────────────────────────────

    def generate_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename to prevent collisions.
        
        📌 WHY UNIQUE FILENAMES?
        Imagine two users upload a file called "report.pdf".
        Without unique names, the second upload would OVERWRITE the first!
        
        📌 HOW WE GENERATE UNIQUE NAMES:
        We use UUID (Universally Unique Identifier) — a 128-bit random
        string that is practically guaranteed to be unique.
        
        Original:  "blood_test.pdf"
        Generated: "a1b2c3d4_blood_test.pdf"
        
        📌 WHAT IS UUID?
        UUID = Universally Unique Identifier
        Example: "550e8400-e29b-41d4-a716-446655440000"
        
        We take the first 8 characters for brevity:
        "550e8400" + "_" + "blood_test.pdf" = "550e8400_blood_test.pdf"
        
        The chance of two UUIDs colliding is astronomically low
        (like winning the lottery multiple times in a row).
        
        Args:
            original_filename: The original name from the user's computer
        
        Returns:
            A unique filename string
        """
        # Generate a short unique prefix (first 8 chars of a UUID)
        unique_prefix = uuid.uuid4().hex[:8]
        
        # Clean the original filename:
        # - Replace spaces with underscores
        # - Keep only safe characters
        safe_name = original_filename.replace(" ", "_")
        
        # Combine: "a1b2c3d4_blood_test.pdf"
        return f"{unique_prefix}_{safe_name}"

    # ──────────────────────────────────────────
    # 3. SAVE FILE TO DISK
    # ──────────────────────────────────────────

    def save_file(self, file: UploadFile, filename: str) -> str:
        """
        Save the uploaded file to the local filesystem.
        
        📌 FILE STORAGE STRATEGY:
        Files are organized by date: uploads/YYYY/MM/filename
        This prevents any single directory from becoming too large.
        
        📌 HOW SAVING WORKS:
        1. Create the directory structure (if it doesn't exist)
        2. Open a new file on disk in write-binary mode ("wb")
        3. Copy the uploaded file's contents to the new file
        4. Return the file path for storing in the database
        
        📌 shutil.copyfileobj():
        This is Python's efficient way to copy file contents.
        It reads the source file in chunks (not all at once)
        so it works well even for large files.
        
        Args:
            file: FastAPI UploadFile object (the uploaded file)
            filename: The unique filename we generated
        
        Returns:
            str: The relative file path where the file was saved
        """
        # Create date-based subdirectory: "uploads/2025/05/"
        now = datetime.now()
        date_dir = UPLOAD_DIR / str(now.year) / f"{now.month:02d}"
        
        # Create all directories in the path (if they don't exist)
        # parents=True  → also create parent directories
        # exist_ok=True → don't error if directory already exists
        date_dir.mkdir(parents=True, exist_ok=True)

        # Full path: "uploads/2025/05/a1b2c3d4_blood_test.pdf"
        file_path = date_dir / filename

        # Save the file to disk
        # "wb" = write binary (files are binary data, not text)
        with open(file_path, "wb") as buffer:
            # Reset file pointer to the beginning before copying
            file.file.seek(0)
            # Copy file contents efficiently in chunks
            shutil.copyfileobj(file.file, buffer)

        # Return the path as a string (stored in the database)
        # We use forward slashes for consistency across OS
        return str(file_path).replace("\\", "/")

    # ──────────────────────────────────────────
    # 4. UPDATE REPORT WITH FILE INFO
    # ──────────────────────────────────────────

    def link_file_to_report(
        self,
        db: Session,
        report_id: int,
        original_filename: str,
        saved_path: str,
        file_size: int,
        file_extension: str,
    ) -> Report | None:
        """
        Update an existing Report record with the uploaded file's metadata.
        
        📌 WHY LINK TO AN EXISTING REPORT?
        The upload workflow is:
        1. User creates a Report (POST /reports) → gets report_id
        2. User uploads a file (POST /upload) → links file to that report_id
        
        This two-step approach is common in real-world APIs because:
        - It separates concerns (metadata vs file data)
        - It allows re-uploading a file without recreating the report
        - It works better with frontend upload progress bars
        
        Args:
            db: Database session
            report_id: The ID of the report to attach the file to
            original_filename: The user's original filename
            saved_path: Where the file was saved on disk
            file_size: Size of the file in bytes
            file_extension: File extension (pdf, jpg, png)
        
        Returns:
            Updated Report object, or None if report not found
        """
        # Find the report in the database
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            return None

        # Update the report's file-related fields
        report.original_filename = original_filename
        report.file_type = file_extension
        report.file_size_bytes = file_size
        report.file_path = saved_path

        # Commit changes and refresh the object to get updated timestamps
        db.commit()
        db.refresh(report)

        return report

    # ──────────────────────────────────────────
    # 5. FULL UPLOAD WORKFLOW (ORCHESTRATOR)
    # ──────────────────────────────────────────

    def process_upload(self, db: Session, report_id: int, file: UploadFile) -> dict:
        """
        Execute the complete file upload workflow.
        
        📌 UPLOAD PIPELINE:
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │   Validate   │ →  │  Save File   │ →  │  Update DB   │
        │  (type/size) │    │  (to disk)   │    │  (report)    │
        └──────────────┘    └──────────────┘    └──────────────┘
        
        If any step fails, we return an error without proceeding further.
        
        📌 FUTURE EXTENSIONS:
        After this pipeline, you'll later add:
        → OCR (extract text from the file)
        → AI Summary (generate a summary from extracted text)
        → Patient Explanation (generate patient-friendly explanation)
        
        Args:
            db: Database session
            report_id: The report to attach this file to
            file: The uploaded file from FastAPI
        
        Returns:
            dict with upload result (success/failure + file info)
        """

        # Step 1: Validate the file
        validation = self.validate_file(file)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
            }

        # Step 2: Generate a unique filename
        unique_name = self.generate_filename(file.filename)

        # Step 3: Save the file to disk
        saved_path = self.save_file(file, unique_name)

        # Step 4: Link the file to the report in the database
        updated_report = self.link_file_to_report(
            db=db,
            report_id=report_id,
            original_filename=file.filename,
            saved_path=saved_path,
            file_size=validation["file_size"],
            file_extension=validation["extension"],
        )

        if not updated_report:
            # Report not found — clean up the saved file
            try:
                os.remove(saved_path)
            except OSError:
                pass  # File cleanup is best-effort
            return {
                "success": False,
                "error": f"Report with ID {report_id} not found.",
            }

        # Step 4.5: If the file is a PDF, automatically extract text and update report status
        if validation["extension"] == "pdf":
            try:
                # 1. Update report status to 'processing'
                logger.info(f"Setting status to 'processing' for report ID {report_id} before extraction...")
                updated_report.status = ReportStatus.PROCESSING
                db.commit()
                db.refresh(updated_report)

                # 2. Extract plain text using PDF utility
                logger.info(f"Starting text extraction from PDF: {saved_path}")
                extracted_text = extract_text_from_pdf(saved_path)

                # 3. Save extracted text
                updated_report.extracted_text = extracted_text
                db.commit()
                db.refresh(updated_report)
                logger.info(f"Successfully saved extracted text for report ID {report_id}. Triggering AI Summarization...")

                # 4. Run AI summarization using the AI service
                try:
                    ai_service.summarize_report(db=db, report_id=report_id)
                    logger.info(f"AI Summarization pipeline successfully completed for report ID {report_id}.")
                except Exception as ai_err:
                    logger.error(
                        f"AI Summarization pipeline failed automatically during upload for report ID {report_id}: {str(ai_err)}"
                    )
                    # Note: The ai_service already updates the report status to FAILED in database.

            except PDFExtractionError as e:
                # Text extraction failed (corrupt file, empty, etc.)
                logger.error(f"PDF text extraction failed for report ID {report_id}: {str(e)}")
                updated_report.status = ReportStatus.FAILED
                db.commit()
                db.refresh(updated_report)
                # Note: We do not fail the upload itself because the file was saved to disk successfully,
                # but the report's processing state is set to 'failed'.

        # Step 5: Return success response
        return {
            "success": True,
            "message": "File uploaded successfully!",
            "file_name": unique_name,
            "original_name": file.filename,
            "file_path": saved_path,
            "file_size_bytes": validation["file_size"],
            "file_type": validation["extension"],
            "report_id": report_id,
        }


# ──────────────────────────────────────────────
# SINGLETON INSTANCE
# ──────────────────────────────────────────────

"""
📌 SINGLETON PATTERN:
  Same as ReportService — we create ONE instance and import it everywhere.
  
  Usage:
    from app.services.upload_service import upload_service
    result = upload_service.process_upload(db, report_id, file)
"""

upload_service = UploadService()
