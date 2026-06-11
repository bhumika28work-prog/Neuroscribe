"""
=============================================================
  app/services/report_service.py — Business Logic Layer
=============================================================

📌 WHAT IS A SERVICE LAYER?
  The service layer contains your BUSINESS LOGIC — the actual
  "work" your application does.

📌 WHY SEPARATE SERVICES FROM ROUTES?
  Without service layer (BAD — "Fat Router" anti-pattern):
  ┌─────────────────────────────────────────┐
  │  @router.post("/reports")               │
  │  async def create_report(data, db):     │
  │      # validate...                      │
  │      # check duplicates...             │
  │      # save to DB...                   │
  │      # send email...                   │
  │      # trigger OCR...                  │
  │      # log activity...  ← 100+ lines!  │
  └─────────────────────────────────────────┘

  With service layer (GOOD — "Thin Router" pattern):
  ┌─────────────────────────────────────────┐
  │  @router.post("/reports")               │
  │  async def create_report(data, db):     │
  │      return report_service.create(data) │  ← 3 lines!
  └─────────────────────────────────────────┘
  
  ✅ Routes stay thin and readable
  ✅ Business logic is reusable (e.g., multiple routes can call the same service)
  ✅ Easier to write unit tests (test services independently)
  ✅ Easier to change logic without touching route definitions

📌 CLEAN ARCHITECTURE LAYERS:
  Route (routes/)         → HTTP layer (receives request, sends response)
       ↓ calls
  Controller (controllers/) → Orchestrates the request
       ↓ calls
  Service (services/)     → Business logic
       ↓ calls
  Database (models/)      → Data persistence
"""

from sqlalchemy.orm import Session
from typing import List, Optional

# Import the Report SQLAlchemy model and Pydantic schemas
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


class ReportService:
    """
    Service class handling all business logic for Reports.

    📌 WHY A CLASS INSTEAD OF FUNCTIONS?
    Using a class allows you to:
    - Group related methods logically
    - Inject dependencies (like a DB session or external API client)
    - Easily mock the whole service in tests
    
    Some developers prefer plain functions — both approaches are valid.
    """

    def get_all_reports(self, db: Session, skip: int = 0, limit: int = 10) -> List[Report]:
        """Retrieve a paginated list of reports.
        
        FastAPI passes `skip` and `limit` calculated from page parameters.
        """
        return db.query(Report).offset(skip).limit(limit).all()

    def get_report_by_id(self, db: Session, report_id: int) -> Optional[Report]:
        """Fetch a single report by primary key.
        
        Returns `None` if no matching record exists.
        """
        return db.query(Report).filter(Report.id == report_id).first()

    def create_report(self, db: Session, report_data: ReportCreate) -> Report:
        """Create and persist a new report.
        
        The `report_data` is a Pydantic model; we convert it to a dict and
        unpack it into the SQLAlchemy `Report` constructor.
        """
        db_report = Report(**report_data.model_dump())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report


    def delete_report(self, db: Session, report_id: int) -> bool:
        """Delete a report by its ID.

        Returns:
            bool: ``True`` if the report was found and deleted, ``False`` otherwise.
        """
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return False
        db.delete(report)
        db.commit()
        return True

    def update_report(self, db: Session, report_id: int, report_data: ReportUpdate) -> Optional[Report]:
        """Update an existing report.
        
        Returns the updated Report object, or None if not found.
        """
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return None
        # Only update fields that were provided (exclude_unset=True)
        update_dict = report_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(report, key, value)
        db.commit()
        db.refresh(report)
        return report



# ──────────────────────────────────────────────
# SINGLETON SERVICE INSTANCE
# ──────────────────────────────────────────────

"""
📌 SINGLETON INSTANCE PATTERN:
  We create ONE instance of ReportService.
  All routes import THIS instance (not the class).
  
  Usage in routes:
    from app.services.report_service import report_service
    result = report_service.get_all_reports(db)
"""

report_service = ReportService()
