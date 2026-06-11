"""
=============================================================
  app/core/config.py — Application Configuration & Settings
=============================================================

📌 WHAT IS THIS FILE?
  This file defines ALL the configuration settings for the app.
  Instead of hardcoding values like database URLs, API keys, etc.
  directly in your code, we load them from a .env file.
  
  This follows the "12-Factor App" methodology — a best practice
  for building modern web applications.

📌 WHY USE ENVIRONMENT VARIABLES?
  ❌ Bad practice (hardcoding secrets):
     DATABASE_URL = "postgresql://admin:password123@localhost/neuroscribe"
     OPENAI_API_KEY = "sk-abc123..."
  
  ✅ Good practice (using .env file):
     DATABASE_URL is stored in .env
     Python reads it using python-dotenv
     Never committed to Git!
  
  This protects your secrets. Imagine pushing your code to GitHub
  with a hardcoded API key — anyone can see and use it!

📌 HOW PYDANTIC SETTINGS WORKS:
  Pydantic reads class fields and automatically loads them
  from environment variables. If an env var is not found,
  it uses the default value you provide.
  
  BaseSettings also automatically reads from your .env file
  (configured in model_config).

📌 COMMON BEGINNER MISTAKE:
  ❌ Don't put .env in Git! Always add .env to .gitignore
  ❌ Don't hardcode API keys directly in Python files
  ✅ Use .env for secrets, config.py for reading them
"""

# pydantic-settings provides BaseSettings which reads from .env files
from pydantic_settings import BaseSettings

# List type for type hints
from typing import List


class Settings(BaseSettings):
    """
    All application settings are defined here.
    
    Pydantic automatically:
    1. Reads these values from environment variables
    2. Falls back to the default values if not found in .env
    3. Validates types (e.g., ensures PORT is an integer, not a string)
    """

    # ──────────────────────────────────────────────
    # APP SETTINGS
    # ──────────────────────────────────────────────

    # Name of the application — shown in API docs
    APP_NAME: str = "NeuroScribe API"
    
    # Version of the API — useful for API versioning
    APP_VERSION: str = "0.1.0"
    
    # Environment: "development", "staging", or "production"
    # This controls behavior like debug mode, logging level, etc.
    ENVIRONMENT: str = "development"
    
    # The port on which the server will run
    # uvicorn will use this value when starting the server
    PORT: int = 8000
    
    # Debug mode: shows detailed error messages
    # ⚠️ Set this to False in production!
    DEBUG: bool = True

    # ──────────────────────────────────────────────
    # DATABASE SETTINGS
    # ──────────────────────────────────────────────

    """
    📌 PostgreSQL Connection URL Format:
    postgresql://<username>:<password>@<host>:<port>/<database_name>
    
    Example:
    postgresql://neuroscribe_user:secret_password@localhost:5432/neuroscribe_db
    
    SQLAlchemy uses this URL to connect to the database.
    We'll set up the actual database connection in a later step.
    """

    # The full PostgreSQL connection string
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/neuroscribe_db"

    # ──────────────────────────────────────────────
    # CORS SETTINGS
    # ──────────────────────────────────────────────

    """
    📌 ALLOWED_ORIGINS:
    This is a list of frontend URLs that are allowed to communicate
    with this backend.
    
    In development: ["*"] allows ALL origins (convenient for testing)
    In production: List your specific frontend URLs for security
    """

    # Default: allow all origins in development
    # In .env, set this as: ALLOWED_ORIGINS=["http://localhost:3000","https://neuroscribe.com"]
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ──────────────────────────────────────────────
    # AI API KEYS (placeholders for now)
    # ──────────────────────────────────────────────

    # Google Gemini API Key — will be used for AI text processing
    # Get yours at: https://makersuite.google.com/
    GEMINI_API_KEY: str = ""
    
    # OpenAI API Key — alternative AI provider
    # Get yours at: https://platform.openai.com/
    OPENAI_API_KEY: str = ""

    # ──────────────────────────────────────────────
    # SECURITY SETTINGS (placeholder for future auth)
    # ──────────────────────────────────────────────

    # Secret key for signing JWT tokens (authentication)
    # Generate a secure one with: openssl rand -hex 32
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    
    # JWT token expiration time in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ──────────────────────────────────────────────
    # FILE UPLOAD SETTINGS
    # ──────────────────────────────────────────────

    # Maximum file size for uploaded reports (in MB)
    MAX_UPLOAD_SIZE_MB: int = 10
    
    # Allowed file types for medical report uploads
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "png", "jpg", "jpeg", "tiff"]

    # ──────────────────────────────────────────────
    # PYDANTIC CONFIGURATION
    # ──────────────────────────────────────────────

    class Config:
        """
        Tells Pydantic WHERE to look for environment variables.
        
        env_file: Path to your .env file
        case_sensitive: Whether env var names are case-sensitive
        """
        env_file = ".env"           # Load from .env file in the project root
        case_sensitive = True       # DATABASE_URL ≠ database_url


# ──────────────────────────────────────────────
# CREATE A SINGLE SETTINGS INSTANCE
# ──────────────────────────────────────────────

"""
📌 SINGLETON PATTERN:
  We create ONE instance of Settings here.
  All other files import THIS instance (not the class).
  
  This ensures that:
  1. Settings are loaded ONCE at startup
  2. All parts of the app use the SAME settings
  3. No duplicate .env file reads
  
  Usage in other files:
    from app.core.config import settings
    print(settings.DATABASE_URL)
"""

settings = Settings()
