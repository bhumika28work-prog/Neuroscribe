"""
=============================================================
  app/models/report.py — SQLAlchemy Model (Database Table)
=============================================================
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum, func
from enum import Enum

# Import the Base declarative class from the database connection module
# We'll create Base in app/database/connection.py
from app.database.connection import Base


# ──────────────────────────────────────────────
# ENUM FOR REPORT STATUS (mirrors Pydantic schema)
# ──────────────────────────────────────────────

class ReportStatus(str, Enum):
    """Possible processing statuses for a medical report."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ──────────────────────────────────────────────
# REPORT MODEL
# ──────────────────────────────────────────────

class Report(Base):
    """SQLAlchemy ORM model for the 'reports' table.
    
    This model defines the database schema that will be created in PostgreSQL.
    It mirrors the Pydantic schemas defined in app/schemas/report.py.
    """

    __tablename__ = "reports"

    # Primary key – auto-incrementing integer
    id = Column(Integer, primary_key=True, index=True)

    # Title provided by the user (required)
    title = Column(String(255), nullable=False, index=True)

    # Original filename of the uploaded PDF/Image
    original_filename = Column(String(255), nullable=True)

    # File metadata – optional until file upload is handled
    file_type = Column(String(50), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # Saved file path on the local server filesystem
    file_path = Column(String(500), nullable=True)

    # OCR extracted text – potentially large
    extracted_text = Column(Text, nullable=True)

    # AI-generated fields – also potentially large
    ai_summary = Column(Text, nullable=True)
    hindi_summary = Column(Text, nullable=True)
    patient_explanation = Column(Text, nullable=True)
    hindi_explanation = Column(Text, nullable=True)

    # Status of the processing pipeline
    status = Column(SAEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING)

    # Timestamp columns – automatically set by PostgreSQL
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        """Human‑readable representation used for debugging and logs."""
        return f"<Report id={self.id} title={self.title!r} status={self.status.value}>"
