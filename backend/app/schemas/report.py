"""
=============================================================
  app/schemas/report.py — Pydantic Schemas (Request/Response)
=============================================================

📌 WHAT IS THIS FILE?
  Pydantic Schemas define the SHAPE of data coming IN and going OUT
  of your API. FastAPI uses these to:
  
  1. VALIDATE incoming request data automatically
     (wrong type? missing field? FastAPI returns a 422 error)
  2. SERIALIZE outgoing response data to JSON
  3. AUTO-GENERATE documentation in /docs

📌 PYDANTIC SCHEMA vs SQLALCHEMY MODEL:
  ┌─────────────────────────────────────────────────────┐
  │             SQLAlchemy Model (app/models/)           │
  │  → Represents a DATABASE TABLE                      │
  │  → Used to READ/WRITE from PostgreSQL               │
  │  → Has Column(), relationship(), etc.               │
  ├─────────────────────────────────────────────────────┤
  │           Pydantic Schema (app/schemas/)             │
  │  → Represents API REQUEST or RESPONSE BODY          │
  │  → Used to VALIDATE input and SERIALIZE output      │
  │  → Has Field(), validators, type hints              │
  └─────────────────────────────────────────────────────┘

📌 WHY SEPARATE SCHEMAS?
  You often want different shapes for different operations:
  
  ReportCreate → What user sends when creating a report
                 (no id, no timestamps — these are auto-generated)
  
  ReportResponse → What you send BACK to the user
                   (includes id, timestamps, status)
  
  ReportUpdate → What user sends to update a report
                 (all fields optional — only update what's sent)

📌 COMMON BEGINNER MISTAKE:
  ❌ Returning SQLAlchemy model objects directly from routes
     (FastAPI can't serialize them to JSON easily)
  ✅ Always return Pydantic schema objects from routes
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ──────────────────────────────────────────────
# ENUM (mirrors the one in models/report.py)
# ──────────────────────────────────────────────

class ReportStatus(str, Enum):
    """Valid statuses for a report — same as in the model."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ──────────────────────────────────────────────
# BASE SCHEMA (shared fields)
# ──────────────────────────────────────────────

class ReportBase(BaseModel):
    """
    Base schema with fields shared by multiple schemas.
    Other schemas inherit from this to avoid repeating fields.
    
    📌 Field(...) vs Field(None):
      Field(...)         → Required field (must be provided)
      Field(None)        → Optional field (defaults to None)
      Field("default")   → Optional with a default value
    
    📌 The `...` (Ellipsis):
      In Pydantic, `...` means "this field is REQUIRED".
      It's Python's Ellipsis literal.
    """
    title: str = Field(
        ...,                            # Required
        min_length=1,                   # Must not be empty
        max_length=255,                 # Max 255 characters
        description="Title of the medical report",
        example="Blood Test Report - John Doe - May 2025"
    )
    original_filename: Optional[str] = Field(
        None,
        description="Original name of the uploaded file",
        example="blood_test.pdf"
    )


# ──────────────────────────────────────────────
# CREATE SCHEMA (for POST requests)
# ──────────────────────────────────────────────

class ReportCreate(ReportBase):
    """
    Schema for creating a new report.
    
    Used when: POST /api/v1/reports
    The user provides only the title (file upload handled separately).
    
    📌 Inherits from ReportBase:
    Gets `title` and `original_filename` for free.
    """
    
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        """
        Custom validator: ensures title isn't just whitespace.
        
        📌 FIELD VALIDATORS:
        Pydantic runs these automatically before saving the value.
        If the validator raises ValueError, Pydantic returns a 422 error.
        """
        if value.strip() == "":
            raise ValueError("Title cannot be blank or only whitespace")
        return value.strip()  # Remove leading/trailing spaces


# ──────────────────────────────────────────────
# UPDATE SCHEMA (for PATCH requests)
# ──────────────────────────────────────────────

class ReportUpdate(BaseModel):
    """
    Schema for updating an existing report.
    
    Used when: PATCH /api/v1/reports/{id}
    ALL fields are Optional — only update what's provided.
    
    📌 WHY Optional for all fields?
    When updating, users might want to update just the title,
    or just the status. Making all fields Optional lets them
    send only the fields they want to change.
    
    This is the PATCH pattern (partial update).
    """
    title: Optional[str] = Field(None, max_length=255)
    status: Optional[ReportStatus] = None


# ──────────────────────────────────────────────
# RESPONSE SCHEMA (for GET responses)
# ──────────────────────────────────────────────

class ReportResponse(ReportBase):
    """
    Schema for report data returned to the client.
    
    Used when: GET /api/v1/reports or GET /api/v1/reports/{id}
    Includes all fields including DB-generated ones (id, timestamps).
    
    📌 model_config with from_attributes=True:
    Tells Pydantic to read data from object attributes
    (e.g., SQLAlchemy model objects) not just dictionaries.
    
    Without this, you'd have to manually convert SQLAlchemy
    objects to dicts before returning them.
    
    With this: FastAPI can directly return a SQLAlchemy model
    and Pydantic will serialize it correctly.
    """
    id: int = Field(..., description="Unique report ID")
    status: ReportStatus = Field(..., description="Processing status")
    file_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    file_path: Optional[str] = Field(None, description="The local path where the file is stored")
    extracted_text: Optional[str] = Field(None, description="Text extracted via OCR")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    hindi_summary: Optional[str] = Field(None, description="AI-generated Hindi summary")
    patient_explanation: Optional[str] = Field(None, description="Patient-friendly explanation")
    hindi_explanation: Optional[str] = Field(None, description="AI-generated Hindi explanation")
    created_at: datetime = Field(..., description="When report was created")
    updated_at: Optional[datetime] = Field(None, description="When report was last updated")

    model_config = {"from_attributes": True}  # Allows reading from SQLAlchemy objects


# ──────────────────────────────────────────────
# LIST RESPONSE SCHEMA
# ──────────────────────────────────────────────

class ReportListResponse(BaseModel):
    """
    Schema for paginated list of reports.
    
    📌 PAGINATION:
    When you have many reports, you don't want to return ALL of them
    at once (could be thousands!). Instead, you return a "page" of
    results with metadata about total count.
    
    Example response:
    {
        "total": 150,
        "page": 1,
        "per_page": 10,
        "reports": [...]
    }
    """
    total: int = Field(..., description="Total number of reports")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of reports per page")
    reports: List[ReportResponse] = Field(..., description="List of reports")


# ──────────────────────────────────────────────
# GENERIC RESPONSE SCHEMAS
# ──────────────────────────────────────────────

class SuccessResponse(BaseModel):
    """Generic success response schema."""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """
    Generic error response schema.
    FastAPI uses this to document error responses in /docs.
    """
    success: bool = False
    error: str
    detail: Optional[str] = None
