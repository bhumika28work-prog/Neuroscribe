"""
=============================================================
  main.py — The Entry Point of the NeuroScribe Backend
=============================================================

📌 WHAT IS THIS FILE?
  This is the STARTING POINT of the entire backend application.
  When you run the server, Python reads this file first.
  Think of it like the "front door" of your backend.

📌 HOW FASTAPI WORKS INTERNALLY (Simplified):
  1. You create a FastAPI() app instance.
  2. You "include" routers (like health, reports, users) into the app.
  3. FastAPI uses Starlette (a web toolkit) under the hood.
  4. When a request comes in, it matches the URL to a route handler.
  5. The handler processes the request and returns a response.

📌 REQUEST-RESPONSE LIFECYCLE:
  Client (Browser/Postman)
      ↓  sends HTTP request (GET /health)
  Uvicorn (receives raw TCP connection)
      ↓  converts to ASGI format
  Starlette (FastAPI's core)
      ↓  applies middleware (e.g., CORS)
  FastAPI Router
      ↓  matches URL to your function
  Your Route Function
      ↓  runs your logic, returns data
  FastAPI
      ↓  converts your return value to JSON response
  Client (gets JSON response back)

📌 WHAT IS UVICORN?
  Uvicorn is an ASGI (Asynchronous Server Gateway Interface) server.
  It sits between the internet and your FastAPI app.
  It handles:
    - Raw HTTP/HTTPS connections
    - WebSockets
    - Multiple requests simultaneously (async)
  
  Think of Uvicorn as the "waiter" who takes orders from customers
  and passes them to the kitchen (FastAPI). FastAPI is the "chef"
  who prepares the food (processes the request and sends a response).

📌 WHY DOES BACKEND ARCHITECTURE MATTER?
  ✅ Maintainability: Easy to find and fix bugs
  ✅ Scalability: Easy to add new features
  ✅ Team Collaboration: Other developers can understand the code
  ✅ Testability: Easier to write unit/integration tests
  ✅ Separation of Concerns: Each file has ONE clear job
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

# FastAPI is the main web framework
# It provides tools to create API endpoints, handle requests, validate data, etc.
from fastapi import FastAPI

# CORSMiddleware allows your frontend (running on a different port/domain)
# to communicate with this backend.
# Without this, browsers will BLOCK requests from different origins.
from fastapi.middleware.cors import CORSMiddleware

# We import our settings (loaded from .env file)
from app.core.config import settings

# We import our routers — each router handles a specific group of endpoints
from app.routes import health, report, upload  # Import health, report, and upload routers

# Import DB engine and Base to auto-create tables on startup
from app.database.connection import engine, Base
from sqlalchemy import text
# Import model to register it in SQLAlchemy metadata
from app.models.report import Report

# ──────────────────────────────────────────────
# CREATE THE FASTAPI APPLICATION INSTANCE
# ──────────────────────────────────────────────

# This creates the main "app" object.
# title, description, version — these show up in the auto-generated API docs at /docs
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🧠 NeuroScribe Backend API
    
    A medical AI assistant that:
    - Accepts medical PDF/image reports
    - Extracts text using OCR
    - Generates AI-powered summaries using Gemini/OpenAI
    - Provides patient-friendly explanations
    """,
    version=settings.APP_VERSION,
    # This is the URL for the API docs (Swagger UI)
    docs_url="/docs",
    # This is an alternative API docs URL (ReDoc)
    redoc_url="/redoc",
)

# ──────────────────────────────────────────────
# CONFIGURE CORS (Cross-Origin Resource Sharing)
# ──────────────────────────────────────────────

"""
📌 WHAT IS CORS?
  Imagine your frontend runs on http://localhost:3000 (React)
  and your backend runs on http://localhost:8000 (FastAPI).
  
  These are DIFFERENT ORIGINS (different ports = different origin).
  
  Browsers have a SECURITY RULE: by default, JavaScript cannot
  make requests to a different origin. This is called the
  "Same-Origin Policy".
  
  CORS is how the BACKEND tells the browser:
  "Hey, it's okay! I allow requests from http://localhost:3000"
  
  allow_origins  → Which websites can talk to this backend
  allow_methods  → Which HTTP methods are allowed (GET, POST, etc.)
  allow_headers  → Which headers are allowed in requests
  allow_credentials → Whether cookies/auth headers are allowed
"""

app.add_middleware(
    CORSMiddleware,
    # In development, we allow all origins with "*"
    # ⚠️ In PRODUCTION, replace "*" with your actual frontend URL
    # Example: ["https://neuroscribe.com", "https://www.neuroscribe.com"]
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    # Allow all standard HTTP methods
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    # Allow all headers (including Authorization, Content-Type, etc.)
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# INCLUDE ROUTERS
# ──────────────────────────────────────────────

"""
📌 WHAT IS A ROUTER?
  Instead of defining ALL routes in main.py (which would make it huge),
  we split them into separate files called "routers".
  
  Each router handles one feature:
  - health.py  → /health endpoint
  - reports.py → /reports endpoints (future)
  - users.py   → /users endpoints (future)
  
  We then "include" these routers here in main.py.
  The prefix="/api/v1" means all routes in that router
  will start with /api/v1/...
  
  Example:
    health router has route "/health"
    After including with prefix="/api/v1"
    Full URL becomes: /api/v1/health
"""

# Include the health check router
app.include_router(
    health.router,
    prefix="/api/v1",    # All routes in this router are prefixed with /api/v1
    tags=["Health"],     # Groups these endpoints under "Health" in the /docs page
)

# Include the report CRUD router
app.include_router(
    report.router,
    prefix="/api/v1",    # All routes in this router are prefixed with /api/v1
    tags=["Reports"],    # Groups these endpoints under "Reports" in the /docs page
)

# Include the upload router
app.include_router(
    upload.router,
    prefix="/api/v1",    # All routes in this router are prefixed with /api/v1
    tags=["Upload"],     # Groups these endpoints under "Upload" in the /docs page
)

# ──────────────────────────────────────────────
# ROOT ENDPOINT
# ──────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint — shows a welcome message.
    This is what you see when you visit http://localhost:8000/ in a browser.
    """
    return {
        "message": "🧠 Welcome to NeuroScribe API",
        "status": "running",
        "docs": "/docs",        # Visit this for interactive API documentation
        "redoc": "/redoc",      # Visit this for alternative API documentation
        "version": settings.APP_VERSION,
    }

# ──────────────────────────────────────────────
# APPLICATION STARTUP & SHUTDOWN EVENTS
# ──────────────────────────────────────────────

"""
📌 LIFESPAN EVENTS:
  These are special hooks that run:
  - On startup: before the server starts accepting requests
  - On shutdown: after the server stops accepting requests
  
  Use these for:
  - Connecting to the database on startup
  - Loading ML models into memory
  - Closing database connections on shutdown
"""

@app.on_event("startup")
async def startup_event():
    """
    Called automatically when the server STARTS.
    Use this to: connect to DB, load models, etc.
    """
    print("🚀 NeuroScribe Backend is starting up...")
    print(f"📝 App Name: {settings.APP_NAME}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"📚 API Docs available at: http://localhost:{settings.PORT}/docs")
    
    # Auto-create all tables in the database on startup
    if engine is not None:
        try:
            print("📦 Creating database tables (if they do not exist)...")
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables checked/created successfully.")
            
            # Check/Add new hindi_explanation & hindi_summary columns dynamically
            with engine.connect() as conn:
                with conn.begin():
                    conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS hindi_explanation TEXT;"))
                    conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS hindi_summary TEXT;"))
            print("✅ Database schema updated with hindi_explanation and hindi_summary columns.")
        except Exception as e:
            print(f"⚠️  Failed to create/migrate database tables on startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Called automatically when the server STOPS.
    Use this to: close DB connections, cleanup resources, etc.
    """
    print("🛑 NeuroScribe Backend is shutting down...")
