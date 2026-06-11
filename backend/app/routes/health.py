"""
=============================================================
  app/routes/health.py — Health Check Endpoint
=============================================================

📌 WHAT IS THIS FILE?
  This file defines the "health check" API route.
  
  A health check endpoint is a simple route that returns
  the current status of the server. It's used by:
  
  - DevOps tools (like Kubernetes, Docker) to know if the
    server is alive and ready to serve requests
  - Monitoring tools to alert when the server goes down
  - Load balancers to know which servers are healthy
  - Developers to quickly test if the server is running

📌 WHAT IS AN ASGI ROUTER?
  Instead of putting all routes in main.py, we create separate
  "router" files. Each APIRouter() is like a mini-app that
  handles a specific group of routes.
  
  Example:
    health.router  → routes like /health, /ping
    reports.router → routes like /reports, /reports/{id}
    users.router   → routes like /users, /users/{id}
  
  All these routers are then "included" in main.py.

📌 WHAT IS async def?
  FastAPI supports both:
  
  def route():        → Synchronous (blocks the thread while running)
  async def route():  → Asynchronous (non-blocking, can handle many requests simultaneously)
  
  Use async def when your route calls:
  - Database queries
  - External API calls (Gemini, OpenAI)
  - File I/O operations
  
  This is one of FastAPI's superpowers — it can handle
  thousands of concurrent requests efficiently!

📌 HOW TO TEST THIS IN POSTMAN:
  1. Open Postman
  2. Create a new request
  3. Set method to: GET
  4. Set URL to: http://localhost:8000/api/v1/health
  5. Click "Send"
  6. You should see the JSON response below

📌 COMMON BEGINNER MISTAKES:
  ❌ Putting ALL routes in main.py (hard to maintain)
  ❌ Not using routers (can't organize endpoints by feature)
  ❌ Using def instead of async def for DB/API calls (slower)
  ✅ Use separate router files for each feature
  ✅ Use async def for database/API operations
"""

# ──────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────

# APIRouter creates a group of routes (like a mini-app)
from fastapi import APIRouter

# datetime for getting the current timestamp
from datetime import datetime

# Our settings to access app configuration
from app.core.config import settings

# ──────────────────────────────────────────────
# CREATE THE ROUTER
# ──────────────────────────────────────────────

"""
📌 APIRouter() creates a new router instance.
  We use this to define routes in separate files.
  
  The router is then "included" in main.py using:
  app.include_router(health.router, prefix="/api/v1", tags=["Health"])
  
  This means all routes here will be accessible at:
  /api/v1/<route_path>
"""

# Create a router instance for health-related endpoints
router = APIRouter()

# ──────────────────────────────────────────────
# HEALTH CHECK ENDPOINT
# ──────────────────────────────────────────────

@router.get(
    "/health",                    # URL path → full URL: /api/v1/health
    summary="Health Check",       # Short description shown in /docs
    description="""
    Returns the current health status of the NeuroScribe API.
    
    Use this endpoint to verify:
    - The server is running
    - The environment is configured correctly
    - Basic system information
    """,
    # response_description tells Swagger UI what a successful response looks like
    response_description="Server is healthy and running",
)
async def health_check():
    """
    Health Check Route
    
    📌 HOW THIS WORKS:
    1. A GET request arrives at /api/v1/health
    2. FastAPI matches it to THIS function (health_check)
    3. The function runs and returns a Python dictionary
    4. FastAPI automatically converts the dictionary to JSON
    5. The JSON response is sent back to the client
    
    📌 HTTP METHODS EXPLAINED:
    GET    → Read/retrieve data (no body)
    POST   → Create new data (with body)
    PUT    → Update entire resource (with body)
    PATCH  → Update part of a resource (with body)
    DELETE → Delete a resource (no body)
    
    Health checks always use GET because we're just READING status.
    
    Returns:
        dict: JSON response with server status and info
    """
    return {
        "status": "healthy",                           # ✅ Server is running
        "message": "🧠 NeuroScribe API is up and running!",
        "app_name": settings.APP_NAME,                 # From our settings
        "version": settings.APP_VERSION,               # API version
        "environment": settings.ENVIRONMENT,           # dev/staging/prod
        "timestamp": datetime.utcnow().isoformat(),    # Current UTC time (ISO format)
        "endpoints": {
            "docs": "/docs",           # Swagger UI - Interactive API docs
            "redoc": "/redoc",         # ReDoc - Alternative API docs
            "health": "/api/v1/health" # This endpoint itself
        }
    }


# ──────────────────────────────────────────────
# PING ENDPOINT (Simple alive check)
# ──────────────────────────────────────────────

@router.get(
    "/ping",
    summary="Ping",
    description="Simple ping endpoint. Returns 'pong' to verify server is alive.",
    response_description="Pong response",
)
async def ping():
    """
    Simple ping endpoint.
    
    The most minimal possible health check.
    Useful for ultra-fast alive checks where you just need
    to know the server is responding.
    
    📌 POSTMAN TEST:
    GET http://localhost:8000/api/v1/ping
    Expected response: {"message": "pong 🏓"}
    """
    return {"message": "pong 🏓"}


# ──────────────────────────────────────────────
# SYSTEM INFO ENDPOINT
# ──────────────────────────────────────────────

@router.get(
    "/info",
    summary="System Information",
    description="Returns detailed system and configuration information.",
    response_description="System information details",
)
async def system_info():
    """
    Returns system configuration info.
    
    ⚠️ NOTE FOR PRODUCTION:
    You may want to REMOVE or PROTECT this endpoint in production
    as it exposes internal configuration details.
    Only expose it in development/staging environments.
    
    📌 POSTMAN TEST:
    GET http://localhost:8000/api/v1/info
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_MB,
        "allowed_file_types": settings.ALLOWED_FILE_TYPES,
        "features": {
            "ocr": "coming soon",           # Will be added in Step 2
            "ai_summary": "coming soon",    # Will be added in Step 3
            "authentication": "coming soon", # Will be added in Step 4
            "database": "placeholder ready", # Connection placeholder is ready
        }
    }
